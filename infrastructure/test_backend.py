import importlib.util
import json
import os
import sys
import unittest
from unittest.mock import patch

os.environ.update({
    'AWS_DEFAULT_REGION': 'us-east-1', 'AWS_REGION': 'us-east-1',
    'AWS_ACCESS_KEY_ID': 'local-test', 'AWS_SECRET_ACCESS_KEY': 'local-test',
    'AWS_EC2_METADATA_DISABLED': 'true',
    'LISTINGS_TABLE': 'test-listings', 'MESSAGES_TABLE': 'test-msgs',
    'CONVERSATIONS_TABLE': 'test-convos', 'RATINGS_TABLE': 'test-ratings',
    'PHOTO_BUCKET': 'test-private-photos', 'SNS_TOPIC': '',
})

class FakeTable:
    def __init__(self, name):
        self.name = name
        self.items = {}
    def put_item(self, Item, **kwargs):
        self.items[Item['listingId']] = Item
    def get_item(self, Key):
        return {'Item': self.items[Key['listingId']]} if Key['listingId'] in self.items else {}
    def query(self, **kwargs):
        return {'Items': list(self.items.values())}

class FakeS3:
    def generate_presigned_post(self, **kwargs):
        return {'url': 'https://example.test/upload', 'fields': {'key': kwargs['Key']}}
    def generate_presigned_url(self, *args, **kwargs):
        return 'https://example.test/photo'

class FakeDynamo:
    def __init__(self):
        self.tables = {}
    def Table(self, name):
        self.tables.setdefault(name, FakeTable(name))
        return self.tables[name]

class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import boto3
        fake = FakeDynamo()
        with patch.object(boto3, 'resource', return_value=fake), patch.object(boto3, 'client', side_effect=lambda name: FakeS3() if name == 's3' else object()):
            spec=importlib.util.spec_from_file_location('backend_test_module', __file__.replace('test_backend.py', 'sharebite_backend.py'))
            cls.backend=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.backend)
        cls.fake = fake
        cls.backend.S3 = FakeS3()

    def event(self, method, path, body=None, sub='test-user'):
        claims={'sub':sub, 'name':'Verified Donor', 'email':'verified@example.test'} if sub else {}
        return {'rawPath':path,'requestContext':{'http':{'method':method},'authorizer':{'jwt':{'claims':claims}}}, 'body': json.dumps(body) if body is not None else None}

    def call(self, event):
        out=self.backend.lambda_handler(event, object())
        return out['statusCode'], json.loads(out['body'])

    def test_public_health(self):
        status,data=self.call(self.event('GET','/health', sub=''))
        self.assertEqual(status,200)
        self.assertEqual(data['status'],'ok')

    def test_denies_missing_verified_identity(self):
        status,data=self.call(self.event('POST','/food',{},sub=''))
        self.assertEqual(status,401)

    def test_add_food_owner_cannot_be_spoofed_and_phone_not_required(self):
        data={'foodName':'Bread','category':'Bakery','description':'Sealed fresh bread',
              'quantity':'2 loaves','location':'Coventry CV1','expiryTime':'2027-01-01T12:00',
              'allergyInfo':'Wheat','ownerUserId':'malicious-spoof','donorName':'Fake','status':'Collected'}
        status,result=self.call(self.event('POST','/food', data))
        self.assertEqual(status,201)
        self.assertEqual(result['item']['ownerUserId'],'test-user')
        self.assertEqual(result['item']['donorName'],'Verified Donor')
        self.assertEqual(result['item']['status'],'Available')
        self.assertNotIn('contactNumber',result['item'])
        self.listing_id=result['item']['listingId']

    def test_invalid_upload_type(self):
        status,result=self.call(self.event('POST','/uploads/presign',{'contentType':'text/html','size':20}))
        self.assertEqual(status,400)

    def test_owner_cannot_rate_own_listing(self):
        record={'listingId':'abcdefab-aaaa-4aaa-aaaa-aaaaaaaaaaaa','ownerUserId':'test-user'}
        self.backend.LISTINGS.items[record['listingId']]=record
        status,result=self.call(self.event('POST','/ratings',{'listingId':record['listingId'],'score':5}))
        self.assertEqual(status,403)

    def test_cannot_message_listing_without_owner_participant(self):
        record={'listingId':'abcdefab-aaaa-4aaa-aaaa-aaaaaaaaaaaa','ownerUserId':'test-user'}
        self.backend.LISTINGS.items[record['listingId']]=record
        status,result=self.call(self.event('POST','/messages',{'listingId':record['listingId'], 'toUserId':'outsider','text':'Hi'},sub='unrelated'))
        self.assertEqual(status,403)

    def test_missing_public_name_never_falls_back_to_email(self):
        data={'foodName':'Vegetables','category':'Produce','description':'Example test',
              'quantity':'2 bags','location':'Public pickup point',
              'expiryTime':'2027-01-01T12:00:00+00:00','allergyInfo':'Confirm with donor'}
        event=self.event('POST','/food',data,sub='donor-private')
        event['requestContext']['authorizer']['jwt']['claims'].pop('name',None)
        status,result=self.call(event)
        self.assertEqual(status,201)
        self.assertEqual(result['item']['donorName'],'ShareBite Member')
        self.assertNotIn('verified@example.test',result['item']['donorName'])

if __name__=='__main__':unittest.main(verbosity=2)
