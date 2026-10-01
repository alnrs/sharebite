# Architecture reconciliation — based on actual project files

Original 603AZ ZIP (`template.yaml`) provisions: AWS Lambda (Python inline code), API Gateway
GET/POST food endpoints, one DynamoDB FoodListings table, SNS, CloudWatch Lambda logging
and a private S3 folder/bucket for front-end files. That original YAML included a role reference
associated with the former lab and **did not provision all services shown in the broader project diagram**.

Separately, your 603AZ code/presentation referenced Cognito authentication and Amplify hosting,
plus proposed CloudFront/WAF/backup enhancements. `Cloud Run` belongs to Google Cloud; here the
relevant AWS website-delivery services are **Amplify** and (optionally) **CloudFront**.

The REVIEWED 604AZ template expands this into Cognito → JWT API Gateway → Lambda → four DynamoDB
tables for listings, conversations, messages and ratings; private S3 donor photos; SNS;
CloudWatch logs/alarms; optional EventBridge expiry Lambda, Secrets Manager message-integrity
key, dashboard, AWS Backup, Amplify scaffold and CloudFront static hosting with optional WAF.

**Important boundaries**
- Optional resources are **not automatically deployed** if their switches were left off.
- An Amplify App/Branch resource is **not equivalent** to connecting GitHub or publishing HTML.
- WAF in this design protects **optional CloudFront static hosting only**, **not** the direct
  API Gateway HTTP endpoint. Do not claim full API WAF protection.
- ShareBite does **not** run on Google Cloud Run.
- `AWS::Lambda::Function.Code.ZipFile` embeds the backend in the CloudFormation stack; editing
  `infrastructure/sharebite_backend.py` alone does not change the deployed Lambda. The
  validator asserts both sources match.
- Stack Outputs required for live frontend connection: Region, ApiBaseUrl,
  CognitoUserPoolId, CognitoAppClientId. AWS generates these; they aren't secret keys.
