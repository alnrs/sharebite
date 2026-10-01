import contextlib
import importlib.util
import io
import os
import unittest
from unittest.mock import patch
os.environ.setdefault('AWS_DEFAULT_REGION','us-east-1')
os.environ.setdefault('AWS_ACCESS_KEY_ID','local-test')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY','local-test')
os.environ.setdefault('LISTINGS_TABLE','test')

class Table:
    def __init__(self):
        self.records=[{'listingId':'abc', 'status':'Available','expiryEpoch':10},
                      {'listingId':'def', 'status':'Available','expiryEpoch':20}]
        self.updated=[]
    def query(self,**kwargs): return {'Items':self.records}
    def update_item(self,**kwargs):self.updated.append(kwargs)

class DDB:
    def __init__(self,t):self.t=t
    def Table(self,name):return self.t

class OptionalTests(unittest.TestCase):
    def test_expiry_worker_updates_only_matching_available_records(self):
        import boto3
        t=Table()
        with patch.object(boto3,'resource', return_value=DDB(t)),patch('time.time',return_value=99):
            spec=importlib.util.spec_from_file_location('expiry','expiry_cleanup.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            with contextlib.redirect_stdout(io.StringIO()):
                result=module.handler({},object())
        self.assertEqual(result,{'checked':2,'expired':2})
        self.assertEqual(len(t.updated),2)
        self.assertEqual(t.updated[0]['ConditionExpression'],'#st = :active AND expiryEpoch <= :now')

    def test_message_secret_is_loaded_server_side_and_cached(self):
        import boto3
        from unittest.mock import Mock
        os.environ.update({'PHOTO_BUCKET':'test','MESSAGES_TABLE':'test-messages',
                           'CONVERSATIONS_TABLE':'test-conversations','RATINGS_TABLE':'test-ratings',
                           'MESSAGE_SECRET_ARN':'arn:fake:secret'})
        fake_secrets=Mock(); fake_secrets.get_secret_value.return_value={'SecretString':'{"key":"example-secret-test"}'}
        with patch.object(boto3,'client',return_value=fake_secrets):
            with patch.object(boto3,'resource',return_value=DDB(Table())):
                spec=importlib.util.spec_from_file_location('api','sharebite_backend.py')
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                self.assertEqual(module.message_signing_key(),b'example-secret-test')
                self.assertEqual(module.message_signing_key(),b'example-secret-test')
                fake_secrets.get_secret_value.assert_called_once()

if __name__=='__main__':unittest.main(verbosity=2)
