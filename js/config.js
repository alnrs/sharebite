/* ShareBite — PUBLIC deployment identifiers from the completed 604AZ CloudFormation Outputs.
   These values identify cloud resources; they are NOT AWS access keys or passwords.
   Verify each ID against the AWS console if sign-in returns a resource-not-found error.
   NEVER put AWS credentials, Cognito session tokens or Secrets Manager values here. */
window.SHAREBITE_CONFIG = Object.freeze({
  mode: 'live',
  region: 'us-east-1',
  apiBaseUrl: 'https://8y6fg62or0.execute-api.us-east-1.amazonaws.com/prod',
  userPoolId: 'us-east-1_eZwIoAqjB',
  userPoolClientId: 'bqjr29947tfaa5sagb0uig0t9'
});
