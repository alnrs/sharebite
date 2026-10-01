"""ShareBite demo API. Source of the CloudFormation inline Lambda code."""
import base64
import hashlib
import hmac
import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer

DDB = boto3.resource('dynamodb')
CLIENT = boto3.client('dynamodb')
S3 = boto3.client('s3')
SNS = boto3.client('sns')
LISTINGS = DDB.Table(os.environ['LISTINGS_TABLE'])
CONVERSATIONS = DDB.Table(os.environ['CONVERSATIONS_TABLE'])
MESSAGES = DDB.Table(os.environ['MESSAGES_TABLE'])
RATINGS = DDB.Table(os.environ['RATINGS_TABLE'])
PHOTO_BUCKET = os.environ['PHOTO_BUCKET']
SNS_TOPIC = os.environ.get('SNS_TOPIC', '')
MESSAGE_SECRET_ARN = os.environ.get('MESSAGE_SECRET_ARN', '')
_MESSAGE_SIGNING_KEY = None


def message_signing_key():
    global _MESSAGE_SIGNING_KEY
    if not MESSAGE_SECRET_ARN:
        return None
    if _MESSAGE_SIGNING_KEY is None:
        secret = boto3.client('secretsmanager').get_secret_value(
            SecretId=MESSAGE_SECRET_ARN)['SecretString']
        _MESSAGE_SIGNING_KEY = json.loads(secret)['key'].encode('utf-8')
    return _MESSAGE_SIGNING_KEY
SER = TypeSerializer()


def response(status, data):
    return {'statusCode': status, 'headers': {'content-type': 'application/json'},
            'body': json.dumps(data, default=str)}


def read_body(event):
    raw = event.get('body') or '{}'
    if event.get('isBase64Encoded'):
        raw = base64.b64decode(raw).decode('utf-8')
    if len(raw) > 16000:
        raise ValueError('Request body is too large')
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError('JSON body must be an object')
    return value


def field(data, key, max_len=200, required=True):
    value = data.get(key, '')
    if not isinstance(value, str):
        raise ValueError(key + ' must be text')
    value = value.strip()
    if (required and not value) or len(value) > max_len:
        raise ValueError('Invalid or missing ' + key)
    return value


def claims_for(event):
    return (event.get('requestContext', {}).get('authorizer', {})
            .get('jwt', {}).get('claims', {}))


def photo_link(item):
    output = dict(item)
    key = output.get('imageKey')
    if key:
        try:
            output['imageUrl'] = S3.generate_presigned_url(
                'get_object', Params={'Bucket': PHOTO_BUCKET, 'Key': key},
                ExpiresIn=900)
        except ClientError:
            output['imageUrl'] = None
    return output


def listing_by_id(listing_id):
    if not re.fullmatch(r'[a-f0-9-]{36}', listing_id):
        return None
    return LISTINGS.get_item(Key={'listingId': listing_id}).get('Item')


def list_food(query):
    limit = min(max(int(query.get('limit') or 40), 1), 50)
    kwargs = {'IndexName': 'StatusIndex',
              'KeyConditionExpression': Key('status').eq('Available'),
              'ScanIndexForward': False, 'Limit': limit}
    if query.get('nextToken'):
        try:
            kwargs['ExclusiveStartKey'] = json.loads(base64.urlsafe_b64decode(
                query['nextToken'].encode('ascii')).decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise ValueError('Invalid nextToken')
    result = LISTINGS.query(**kwargs)
    items = [photo_link(i) for i in result.get('Items', [])]
    if query.get('format') == 'paged':
        marker = result.get('LastEvaluatedKey')
        token = base64.urlsafe_b64encode(json.dumps(marker).encode()).decode() if marker else None
        return {'items': items, 'nextToken': token}
    return items  # Backward-compatible with current dashboard and browse pages.


def add_food(data, claims):
    record = {k: field(data, k, n) for k, n in (
        ('foodName', 120), ('category', 60), ('description', 2000),
        ('quantity', 80), ('location', 160), ('expiryTime', 40),
        ('allergyInfo', 1200))}
    record['storageInstructions'] = field(data, 'storageInstructions', 1000, False)
    # The owner and public donor name come from VERIFIED claims, not the browser.
    owner = claims['sub']
    record['ownerUserId'] = owner
    record['donorName'] = str(claims.get('name') or 'ShareBite Member')[:120]
    record['listingId'] = str(uuid.uuid4())
    record['status'] = 'Available'
    record['createdAt'] = datetime.now(timezone.utc).isoformat()
    # Old HTML datetime-local sends no timezone; don't guess. The next frontend
    # update should send new Date(expiryTime.value).toISOString() with an offset.
    try:
        deadline = datetime.fromisoformat(record['expiryTime'].replace('Z', '+00:00'))
        if deadline.tzinfo is not None:
            record['expiryEpoch'] = int(deadline.timestamp())
    except ValueError:
        raise ValueError('Invalid expiryTime timestamp')
    image_key = field(data, 'imageKey', 256, False)
    if image_key:
        if not image_key.startswith('users/' + owner + '/uploads/'):
            raise ValueError('Image is not owned by this account')
        try:
            S3.head_object(Bucket=PHOTO_BUCKET, Key=image_key)
        except ClientError:
            raise ValueError('Image upload has not completed')
        record['imageKey'] = image_key
    LISTINGS.put_item(Item=record, ConditionExpression='attribute_not_exists(listingId)')
    notification = 'disabled'
    if SNS_TOPIC:
        try:
            SNS.publish(TopicArn=SNS_TOPIC, Subject='New ShareBite listing',
                        Message='A new food donation listing has been created.')
            notification = 'published'
        except ClientError:
            notification = 'unavailable'
    return {'message': 'Food listing added successfully', 'item': photo_link(record),
            'notification': notification}


def my_food(owner):
    result = LISTINGS.query(IndexName='OwnerIndex',
                            KeyConditionExpression=Key('ownerUserId').eq(owner),
                            ScanIndexForward=False, Limit=50)
    return [photo_link(i) for i in result.get('Items', [])]


def update_food(listing_id, data, owner):
    status = field(data, 'status', 16)
    if status not in ('Available', 'Reserved', 'Collected', 'Removed'):
        raise ValueError('Invalid listing status')
    try:
        LISTINGS.update_item(Key={'listingId': listing_id},
                             UpdateExpression='SET #st = :s',
                             ConditionExpression='ownerUserId = :o',
                             ExpressionAttributeNames={'#st': 'status'},
                             ExpressionAttributeValues={':s': status, ':o': owner})
    except CLIENT.exceptions.ConditionalCheckFailedException:
        return None
    return {'message': 'Listing status updated', 'status': status}


def prepare_upload(data, owner):
    content_type = field(data, 'contentType', 40)
    extensions = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp'}
    if content_type not in extensions:
        raise ValueError('Only JPG, PNG and WebP photos are allowed')
    size = data.get('size')
    if not isinstance(size, int) or not 0 < size <= 5242880:
        raise ValueError('Photo must be between 1 byte and 5 MB')
    key = 'users/' + owner + '/uploads/' + str(uuid.uuid4()) + extensions[content_type]
    post = S3.generate_presigned_post(
        Bucket=PHOTO_BUCKET, Key=key,
        Fields={'Content-Type': content_type},
        Conditions=[{'Content-Type': content_type}, ['content-length-range', 1, 5242880]],
        ExpiresIn=300)
    return {'uploadUrl': post['url'], 'fields': post['fields'], 'imageKey': key,
            'maxBytes': 5242880}


def thread_id(listing_id, user_a, user_b):
    participants = '|'.join(sorted((user_a, user_b)))
    return hashlib.sha256((listing_id + '|' + participants).encode()).hexdigest()


def typed(record):
    return {k: SER.serialize(v) for k, v in record.items()}


def send_message(data, sender):
    listing_id = field(data, 'listingId', 40)
    other = field(data, 'toUserId', 100)
    body = field(data, 'text', 2000)
    listing = listing_by_id(listing_id)
    if not listing:
        return 404, {'message': 'Listing not found'}
    if other == sender:
        raise ValueError('Cannot message yourself')
    if listing['ownerUserId'] not in (sender, other):
        return 403, {'message': 'Conversation must include the listing owner'}
    thread = thread_id(listing_id, sender, other)
    now = datetime.now(timezone.utc).isoformat()
    message_id = now + '#' + str(uuid.uuid4())
    msg = {'threadId': thread, 'messageId': message_id,
           'senderUserId': sender, 'recipientUserId': other,
           'listingId': listing_id, 'text': body, 'sentAt': now}
    # Optional server-side message-integrity marker, not a substitute for encryption.
    signing_key = message_signing_key()
    if signing_key:
        canonical = json.dumps(msg, sort_keys=True, separators=(',', ':')).encode()
        msg['integrityHmac'] = hmac.new(signing_key, canonical, hashlib.sha256).hexdigest()
    # One transaction keeps the message and both participants' inboxes in sync.
    transact = [{'Put': {'TableName': MESSAGES.name, 'Item': typed(msg),
                         'ConditionExpression': 'attribute_not_exists(messageId)'}}]
    for person, peer in ((sender, other), (other, sender)):
        transact.append({'Update': {
            'TableName': CONVERSATIONS.name,
            'Key': typed({'userId': person, 'threadId': thread}),
            'UpdateExpression': ('SET peerUserId=:peer, listingId=:listing, '
                                 'updatedAt=:time, lastMessage=:preview'),
            'ExpressionAttributeValues': typed({
                ':peer': peer, ':listing': listing_id, ':time': now,
                ':preview': body[:100]}),
        }})
    CLIENT.transact_write_items(TransactItems=transact)
    return 201, {'message': 'Message sent', 'threadId': thread, 'messageId': message_id}


def get_inbox(owner):
    result = CONVERSATIONS.query(KeyConditionExpression=Key('userId').eq(owner), Limit=50)
    return sorted(result.get('Items', []), key=lambda x: x['updatedAt'], reverse=True)


def read_thread(query, owner):
    thread = field(query, 'threadId', 64)
    membership = CONVERSATIONS.get_item(Key={'userId': owner, 'threadId': thread}).get('Item')
    if not membership:
        return 403, {'message': 'You cannot access this conversation'}
    result = MESSAGES.query(KeyConditionExpression=Key('threadId').eq(thread),
                            ScanIndexForward=False, Limit=50)
    return 200, list(reversed(result.get('Items', [])))


def write_rating(data, user):
    listing_id = field(data, 'listingId', 40)
    score = data.get('score')
    if type(score) is not int or score < 1 or score > 5:
        raise ValueError('Rating must be an integer between 1 and 5')
    listing = listing_by_id(listing_id)
    if not listing:
        return 404, {'message': 'Listing not found'}
    if user == listing['ownerUserId']:
        return 403, {'message': 'You cannot rate your own listing'}
    item = {'listingId': listing_id, 'reviewerUserId': user, 'score': score,
            'createdAt': datetime.now(timezone.utc).isoformat()}
    try:
        RATINGS.put_item(Item=item, ConditionExpression='attribute_not_exists(reviewerUserId)')
    except CLIENT.exceptions.ConditionalCheckFailedException:
        return 409, {'message': 'You have already rated this listing'}
    return 201, {'message': 'Rating recorded'}


def get_ratings(listing_id):
    if not listing_by_id(listing_id):
        return 404, {'message': 'Listing not found'}
    scores = []
    kwargs = {'KeyConditionExpression': Key('listingId').eq(listing_id)}
    while True:
        result = RATINGS.query(**kwargs)
        scores.extend(int(i['score']) for i in result.get('Items', []))
        if not result.get('LastEvaluatedKey'):
            break
        kwargs['ExclusiveStartKey'] = result['LastEvaluatedKey']
    return 200, {'count': len(scores), 'average': round(sum(scores) / len(scores), 2)
                 if scores else None}


def lambda_handler(event, context):
    request_id = getattr(context, 'aws_request_id', 'unknown')
    method = event.get('requestContext', {}).get('http', {}).get('method', '')
    path = event.get('rawPath') or '/'
    query = event.get('queryStringParameters') or {}
    if method == 'GET' and path == '/health':
        return response(200, {'status': 'ok', 'note': 'API process health only'})
    claims = claims_for(event)
    if not claims.get('sub'):
        return response(401, {'message': 'Verified authentication required'})
    owner = claims['sub']
    try:
        if method == 'GET' and path == '/food':
            return response(200, list_food(query))
        if method == 'POST' and path == '/food':
            return response(201, add_food(read_body(event), claims))
        if method == 'GET' and path == '/my-food':
            return response(200, my_food(owner))
        if path.startswith('/food/') and method in ('GET', 'PATCH'):
            listing_id = path.removeprefix('/food/')
            if method == 'GET':
                item = listing_by_id(listing_id)
                if item and (item.get('status') == 'Available' or item.get('ownerUserId') == owner):
                    return response(200, photo_link(item))
                return response(404, {'message': 'Listing not found'})
            if not listing_by_id(listing_id):
                return response(404, {'message': 'Listing not found'})
            result = update_food(listing_id, read_body(event), owner)
            return response(200 if result else 403, result or {'message': 'Not your listing'})
        if method == 'POST' and path == '/uploads/presign':
            return response(200, prepare_upload(read_body(event), owner))
        if method == 'GET' and path == '/conversations':
            return response(200, get_inbox(owner))
        if method == 'GET' and path == '/messages':
            status, result = read_thread(query, owner)
            return response(status, result)
        if method == 'POST' and path == '/messages':
            status, result = send_message(read_body(event), owner)
            return response(status, result)
        if method == 'GET' and path == '/ratings':
            status, result = get_ratings(field(query, 'listingId', 40))
            return response(status, result)
        if method == 'POST' and path == '/ratings':
            status, result = write_rating(read_body(event), owner)
            return response(status, result)
        if method == 'GET' and path == '/me':
            return response(200, {'userId': owner, 'name': claims.get('name', ''),
                                  'email': claims.get('email', '')})
        return response(404, {'message': 'Route not found'})
    except (ValueError, json.JSONDecodeError) as error:
        return response(400, {'message': str(error)})
    except ClientError as error:
        # Do not expose AWS internal errors to the browser.
        print(json.dumps({'type': 'aws_error', 'code': error.response.get('Error', {}).get('Code'),
                          'requestId': request_id}))
        return response(503, {'message': 'Service temporarily unavailable', 'requestId': request_id})
    except Exception as error:
        print(json.dumps({'type': 'unhandled', 'error': str(error), 'requestId': request_id}))
        return response(500, {'message': 'Internal service error', 'requestId': request_id})
