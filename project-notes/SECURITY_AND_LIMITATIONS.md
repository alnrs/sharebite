# Security, privacy, deployment and safety review

1. **Privacy fix in REVIEWED template (not automatically deployed).** The earlier premium Lambda
   computed a listing's `donorName` from Cognito `name` **OR the donor email**. The browser hid
   some labels, but an authenticated user could inspect API JSON. The REVIEWED template changes
   the fallback to the generic name `ShareBite Member`. To apply it, create/review a CloudFormation
   change set against your **existing stack** with the same parameters. Already-stored listing
   records containing email-based donor names will **not** be automatically anonymised; review
   and correct test records. Do not use real personal information until privacy is reviewed.
2. **Do not paste credentials.** Frontend configuration includes only *public* `ApiBaseUrl`,
   `CognitoUserPoolId`, public `CognitoAppClientId` and Region. Never supply AWS access keys,
   secret access keys, session tokens, Cognito tokens, private API keys, Secrets Manager values,
   or your university account credentials.
3. **No phone number exposure.** Current food form does not request phone numbers; messages
   work inside authenticated ShareBite. However, **no automatic content moderation** prevents
   users from typing contact details in descriptions or messages. Add policy/moderation before
   production use; evaluate safeguarding, food hygiene, allergy and collection processes.
4. **Live browsing requires authentication** due the deployed `/food` JWT authorizer. The landing
   page can be public; live donation content is shown after sign-in.
5. **CORS uses ONE origin.** Exact local `http://localhost:5500` and published Amplify HTTPS
   origin require separate CloudFormation `FrontendOrigin` parameter updates; no production `*`.
   API Gateway and S3 bucket must both reflect actual browser origin.
6. **Backend limitations:** no recipient reservations, no authenticated profile edits, no
   WebSocket/live push, no image malware/content moderation, and ratings aren't verified by
   actual completed food collection. Keep prototype wording in university reports.
7. **Existing lab permissions:** the template may include advanced options that are unavailable
   or chargeable in AWS Academy. Confirm enabled Resources and Events, avoid enabling everything
   for a first deployment, and budget for any retained S3/DynamoDB/backup resources.
8. **Testing boundary:** structural/backend/mock-JS tests are local and do not establish an
   end-to-end, real-AWS successful service or security audit. Perform two-user manual tests and
   inspect CloudWatch before describing a feature as deployed and working.
9. **Cognito dependency:** the browser currently loads Cognito Identity JS v6.3.15 from an
   external CDN in *live* mode. For higher availability/security in production, vendor/pin the
   audited dependency in your own build pipeline and configure a suitable CSP.
