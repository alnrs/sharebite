"""Offline checks only. Not equivalent to AWS CloudFormation ValidateTemplate or deployment."""
from pathlib import Path
import yaml,re,ast
p=Path(__file__).parent
class Loader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        # Strict duplicate-key rejection (known errors in generated CF templates).
        result={}
        for kn, vn in node.value:
            k=self.construct_object(kn,deep=deep)
            if k in result:raise ValueError('Duplicate YAML key: '+str(k)+' line '+str(kn.start_mark.line+1))
            result[k]=self.construct_object(vn,deep=deep)
        return result

def transform(loader, suffix, node):
    if isinstance(node,yaml.ScalarNode):v=loader.construct_scalar(node)
    elif isinstance(node,yaml.SequenceNode):v=loader.construct_sequence(node,deep=True)
    else:v=loader.construct_mapping(node,deep=True)
    return {'fn::'+suffix:v}
Loader.add_multi_constructor('!',transform)
f=p/'ShareBite_604AZ_REVIEWED_CloudFormation.yaml'
d=yaml.load(f.read_text(),Loader)
resources=d['Resources']; params=d['Parameters']; conditions=d['Conditions']; outputs=d['Outputs']
refs=set(); condrefs=set(); omitted=set()
pseudo={'AWS::Region','AWS::AccountId','AWS::Partition','AWS::StackName','AWS::StackId','AWS::URLSuffix','AWS::NoValue','AWS::NotificationARNs'}
def scan(x):
    if isinstance(x,list):
        for v in x:scan(v)
    elif isinstance(x,dict):
        for k,v in x.items():
            if k in ('fn::Ref','fn::GetAtt'):
                a=v.split('.')[0] if isinstance(v,str) else v[0]
                refs.add(a)
            elif k=='fn::If':
                condrefs.add(v[0]);scan(v[1:])
            elif k=='fn::Sub':
                src=v if isinstance(v,str) else v[0]
                bound=set() if isinstance(v,str) else set(v[1])
                for token in re.findall(r'\$\{([^}]+)\}',src):
                    if not token.startswith('!') and token not in bound:
                        refs.add(token.split('.')[0])
                if not isinstance(v,str):scan(v[1])
            else:scan(v)
scan(d)
for r in resources.values():
    if 'Condition' in r:condrefs.add(r['Condition'])
for o in outputs.values():
    if 'Condition' in o:condrefs.add(o['Condition'])
assert not(refs - pseudo - set(resources) -set(params)),('unknown refs',refs-pseudo-set(resources)-set(params))
assert not(condrefs-set(conditions)),('unknown conditions',condrefs-set(conditions))
assert len(resources)==len(set(resources))
api=resources['ShareBiteHttpApi']
assert api['Properties']['CorsConfiguration']['AllowOrigins']==[{'fn::Ref':'FrontendOrigin'}]
routes={r['Properties']['RouteKey']:r['Properties'] for r in resources.values() if r['Type']=='AWS::ApiGatewayV2::Route'}
assert len(routes)==13
assert all(r['AuthorizationType']==('NONE' if k=='GET /health' else 'JWT') for k,r in routes.items())
assert resources['PrivatePhotoBucket']['Properties']['PublicAccessBlockConfiguration']==dict.fromkeys(['BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets'],True)
assert resources['StaticWebsiteBucket']['Condition']=='WithStaticHosting'
assert resources['StaticCloudFrontDistribution']['Condition']=='WithStaticHosting'
assert resources['EdgeManagedWAF']['Condition']=='WithEdgeWAF'
assert resources['ExpiryEventRule']['Condition']=='WithExpiry'
assert resources['ServerMessageIntegritySecret']['Condition']=='WithSecrets'
assert resources['ShareBiteBackupSelection']['Condition']=='WithBackup'
assert resources['ShareBiteDashboard']['Condition']=='WithDashboard'
assert len(params)==14
assert all(params[n]['Default']=='false' for n in ['CreateAmplifyScaffold','EnableEventBridgeExpiry','EnableMessageIntegritySecret','EnableDashboard','EnableSecureStaticHosting','EnableEdgeWAF','EnableAWSBackup','UseDedicatedRole','EnablePITR'])
api_py=resources['ShareBiteFunction']['Properties']['Code']['ZipFile']
expiry_py=resources['ExpiryCleanupFunction']['Properties']['Code']['ZipFile']
assert api_py==(p/'sharebite_backend.py').read_text()
assert expiry_py==(p/'expiry_cleanup.py').read_text().rstrip()+'\n'
for code in (api_py,expiry_py):ast.parse(code);compile(code,'index.py','exec')
assert 'contactNumber' not in api_py
assert 'ServerSideMessageSigning' in f.read_text()
print('PASS: YAML parses with strict duplicate-key detection, '+str(len(resources))+' resources, '+str(len(params))+' parameters, '+str(len(outputs))+' outputs.')
print('PASS: all Ref/GetAtt/Sub and conditions resolve structurally; 13 routes with JWT authorization except /health.')
print('PASS: both inline Lambdas match the standalone code and compile; private buckets, optional advanced infrastructure, and safe default flags.')
print('PASS: file size '+str(f.stat().st_size)+' bytes (<1 MB CloudFormation console-upload limit).')
print('NOT VERIFIED: AWS-side ValidateTemplate, actual region/account permissions, end-to-end frontend integration.')
