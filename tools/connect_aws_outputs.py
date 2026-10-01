#!/usr/bin/env python3
"""Configure ShareBite's PUBLIC browser settings from CloudFormation Outputs.
Do not supply AWS keys, tokens, passwords or private Secrets Manager values.
Usage: python scripts/configure_frontend.py --outputs-file outputs.json
   OR: python scripts/configure_frontend.py (guided public-value prompts)
outputs.json may be AWS CLI describe-stacks JSON or an object keyed by OutputKey.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'js'/'config.js'
EXPECTED={'apiBaseUrl':'ApiBaseUrl','userPoolId':'CognitoUserPoolId',
          'userPoolClientId':'CognitoAppClientId','region':'Region'}
def read_outputs(filename):
    obj=json.loads(Path(filename).read_text(encoding='utf-8'))
    if isinstance(obj,dict) and 'Stacks' in obj:
        if len(obj['Stacks'])!=1: raise ValueError('Specify only one stack in the Outputs file.')
        obj=obj['Stacks'][0].get('Outputs',[])
    if isinstance(obj,dict) and 'Outputs' in obj:obj=obj['Outputs']
    if isinstance(obj,list):obj={r['OutputKey']:r['OutputValue'] for r in obj}
    if not isinstance(obj,dict): raise ValueError('Expected an Outputs object or list from one stack.')
    return obj
def main():
    p=argparse.ArgumentParser(description='Apply new public AWS Stack Outputs to js/config.js.')
    p.add_argument('--outputs-file',help='JSON copied/exported from your completed CloudFormation stack.')
    p.add_argument('--api',help='Stack Output: ApiBaseUrl (not FoodApiUrl)')
    p.add_argument('--pool',help='Stack Output: CognitoUserPoolId')
    p.add_argument('--client',help='Stack Output: CognitoAppClientId, public client')
    p.add_argument('--region',default='us-east-1',help='Stack Output: Region')
    args=p.parse_args()
    if args.outputs_file:
        o=read_outputs(args.outputs_file)
        data={name:o.get(out,'') for name,out in EXPECTED.items()}
    else:
        print('Enter PUBLIC CloudFormation Outputs. Never paste AWS access or secret keys.')
        data={'apiBaseUrl':args.api or input('ApiBaseUrl: ').strip(),
              'userPoolId':args.pool or input('CognitoUserPoolId: ').strip(),
              'userPoolClientId':args.client or input('CognitoAppClientId: ').strip(),
              'region':args.region}
    data['region']=data['region'] or 'us-east-1'
    api=data['apiBaseUrl'].strip().rstrip('/')
    parsed=urlsplit(api)
    if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('ApiBaseUrl must be an HTTPS API base URL with no username, query or fragment.')
    if not re.fullmatch(r'[a-z]{2}(?:-[a-z]+)+-[0-9]',data['region']):
        raise ValueError('Unexpected region. Example: us-east-1.')
    if not re.fullmatch(re.escape(data['region'])+r'_[A-Za-z0-9]+',data['userPoolId']):
        raise ValueError('Cognito pool ID should start with '+data['region']+'_ . Verify region/stack.')
    if not re.fullmatch(r'[A-Za-z0-9]{8,128}',data['userPoolClientId']):
        raise ValueError('Enter the PUBLIC Cognito App Client ID, not a client secret.')
    for k,v in data.items():
        if re.search(r'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|-----BEGIN PRIVATE KEY-----',v):
            raise ValueError('A secret or AWS credential was detected. Refusing to write it into website code.')
    data['apiBaseUrl']=api
    contents=('/* PUBLIC frontend configuration. Never add AWS credentials, Tokens, or Secrets Manager values. */\n'
              'window.SHAREBITE_CONFIG = Object.freeze('+json.dumps({'mode':'live',**data},indent=2)+' );\n')
    DEST.write_text(contents,encoding='utf-8')
    print('Wrote live configuration to js/config.js. No credentials needed.')
    print('NEXT: make sure your stack FrontendOrigin matches the EXACT domain+scheme of the site. '+
          'Then run tools/create_amplify_zip.py to make the LIVE site upload.')
if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError,KeyError,json.JSONDecodeError) as exc:
        print('CONFIGURATION ERROR:',exc,file=sys.stderr);sys.exit(1)
