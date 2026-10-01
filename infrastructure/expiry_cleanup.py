"""EventBridge optional expiration maintenance for timezone-aware food listings."""
import json
import os
import time
from datetime import datetime, timezone
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

T = boto3.resource('dynamodb').Table(os.environ['LISTINGS_TABLE'])

def handler(event, context):
    now = int(time.time())
    expired = 0
    checked = 0
    options = {'IndexName':'ExpiryIndex',
               'KeyConditionExpression':Key('status').eq('Available') & Key('expiryEpoch').lte(now),
               'Limit':50, 'ProjectionExpression':'listingId, #st, expiryEpoch',
               'ExpressionAttributeNames':{'#st':'status'}}
    while checked < 200:
        results = T.query(**options)
        for item in results.get('Items', []):
            checked += 1
            try:
                T.update_item(Key={'listingId':item['listingId']},
                  ConditionExpression='#st = :active AND expiryEpoch <= :now',
                  UpdateExpression='SET #st = :expired',
                  ExpressionAttributeNames={'#st':'status'},
                  ExpressionAttributeValues={':active':'Available', ':expired':'Expired', ':now':now})
                expired += 1
            except ClientError as exc:
                if exc.response.get('Error',{}).get('Code')!='ConditionalCheckFailedException':
                    raise
        marker = results.get('LastEvaluatedKey')
        if not marker or checked >= 200:
            break
        options['ExclusiveStartKey'] = marker
    print(json.dumps({'event':'expiry_cleanup','checked':checked,'expired':expired,
                      'utc':datetime.now(timezone.utc).isoformat()}))
    return {'checked':checked,'expired':expired}
