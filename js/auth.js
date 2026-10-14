/* ShareBite browser-to-Cognito authentication.
 * Uses the public Cognito User Pools HTTPS APIs directly, rather than downloading
 * a script from a third-party CDN. USER_PASSWORD_AUTH is enabled by our template.
 * Session tokens are kept in SESSION storage, not in source files or Git.
 * The API Gateway JWT authorizer, not this browser code, is the security boundary.
 */
const cfg = () => window.SHAREBITE_CONFIG;
export const isDemo = () => cfg().mode !== 'live';
const DEMO_KEY = 'sharebite604-demo-user';
const SESSION_KEY = 'sharebite604-cognito-session-v2';
const requireConfig = () => {
  const c = cfg();
  if (!c?.apiBaseUrl || !c?.userPoolId || !c?.userPoolClientId || !c?.region) {
    throw new Error('AWS configuration is incomplete. Check js/config.js against the CloudFormation Outputs.');
  }
  if (!c.userPoolId.startsWith(c.region + '_')) throw new Error('Cognito pool and region do not match.');
};
function decodeJwt(jwt) {
  if (typeof jwt !== 'string' || jwt.split('.').length !== 3) throw new Error('Unexpected Cognito token.');
  const part = jwt.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
  return JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(part), c => c.charCodeAt(0))));
}
function saveTokens(result, previous = null) {
  requireConfig();
  if (!result?.IdToken || !result?.AccessToken) throw new Error('Cognito did not return a complete sign-in session.');
  const claims = decodeJwt(result.IdToken);
  const expectedIssuer = `https://cognito-idp.${cfg().region}.amazonaws.com/${cfg().userPoolId}`;
  // These are PUBLIC identity claims, not a token or password. Keep validation strict.
  if (claims.iss !== expectedIssuer) {
    throw new Error(`Cognito user-pool mismatch. Your js/config.js expects ${expectedIssuer}, but Cognito issued a token for ${String(claims.iss || 'missing issuer')}. Copy the exact User Pool ID from your CURRENT AWS CloudShell output into js/config.js.`);
  }
  if (claims.aud !== cfg().userPoolClientId) {
    throw new Error(`Cognito app-client mismatch. Your js/config.js expects ${cfg().userPoolClientId}; the returned token identifies ${String(claims.aud || 'missing audience')}. Copy the exact app-client ID from AWS.`);
  }
  if (claims.token_use !== 'id') {
    throw new Error('Cognito returned a token of the wrong type. Sign-in requires an ID token.');
  }
  const tokens = { idToken: result.IdToken, accessToken: result.AccessToken,
    refreshToken: result.RefreshToken || previous?.refreshToken || null };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(tokens));
  return { claims, jwt: tokens.idToken };
}
async function cognito(action, body) {
  requireConfig();
  const endpoint = `https://cognito-idp.${cfg().region}.amazonaws.com/`;
  let response;
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type':'application/x-amz-json-1.1',
        'X-Amz-Target':`AWSCognitoIdentityProviderService.${action}` },
      body: JSON.stringify(body), signal: AbortSignal.timeout(20000)
    });
  } catch (error) {
    throw new Error('Unable to reach Cognito. Check your internet connection, region and browser console.');
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const code = String(data.__type || data.code || '').split('#').pop();
    const common = {
      NotAuthorizedException: 'Cognito rejected this sign-in request (incorrect username or password). This is not a token-expiry error. Use the account that succeeded in the AWS CloudShell test.',
      UserNotConfirmedException: 'Confirm your account using the email code before signing in.',
      UsernameExistsException: 'An account with this email already exists.',
      CodeMismatchException: 'That verification code is incorrect. Try again.',
      ExpiredCodeException: 'Your code has expired. Request another.',
      InvalidPasswordException: 'Password must contain 12+ characters, uppercase, lowercase, number and symbol.',
      TooManyRequestsException: 'Too many attempts. Wait before trying again.',
      LimitExceededException: 'Too many requests. Try again later.'
    };
    throw new Error(common[code] || String(data.message || data.Message || code || 'Cognito request failed.'));
  }
  return data;
}
export async function currentSession() {
  if (isDemo()) {
    const raw = sessionStorage.getItem(DEMO_KEY);
    if (!raw) return null;
    const profile = JSON.parse(raw);
    return { claims:{sub:'demo-user',email:profile.email,name:profile.name || 'Preview member'},jwt:'demo-only' };
  }
  requireConfig();
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  let tokens;
  try { tokens = JSON.parse(raw); } catch { sessionStorage.removeItem(SESSION_KEY); return null; }
  try {
    const claims = decodeJwt(tokens.idToken);
    const issuer = `https://cognito-idp.${cfg().region}.amazonaws.com/${cfg().userPoolId}`;
    if (claims.iss !== issuer || claims.aud !== cfg().userPoolClientId || claims.token_use !== 'id') {
      sessionStorage.removeItem(SESSION_KEY); return null;
    }
    if (claims.exp > Math.floor(Date.now() / 1000) + 90) return { claims, jwt:tokens.idToken };
    if (!tokens.refreshToken) { sessionStorage.removeItem(SESSION_KEY); return null; }
    const answer = await cognito('InitiateAuth', { AuthFlow:'REFRESH_TOKEN_AUTH', ClientId:cfg().userPoolClientId,
      AuthParameters:{REFRESH_TOKEN:tokens.refreshToken} });
    return saveTokens(answer.AuthenticationResult, tokens);
  } catch {
    sessionStorage.removeItem(SESSION_KEY);
    return null;
  }
}
export async function requireSession(next='dashboard.html') {
  const s = await currentSession();
  if (!s) { location.replace('login.html?next=' + encodeURIComponent(next)); return null; }
  return s;
}
export async function signIn(email, password) {
  if (isDemo()) {
    if (!email || !password) throw new Error('Enter an email and password for the preview.');
    sessionStorage.setItem(DEMO_KEY,JSON.stringify({email,name:email.split('@')[0].replace(/[._-]/g,' ')}));
    return;
  }
  const result = await cognito('InitiateAuth', { AuthFlow:'USER_PASSWORD_AUTH', ClientId:cfg().userPoolClientId,
    AuthParameters:{USERNAME:email.trim(),PASSWORD:password} });
  if (result.ChallengeName) throw new Error('This account requires an additional verification or password challenge not configured in the prototype.');
  return saveTokens(result.AuthenticationResult);
}
export async function register(name,email,password) {
  if (isDemo()) { sessionStorage.setItem(DEMO_KEY,JSON.stringify({name,email})); return {preview:true}; }
  return cognito('SignUp', { ClientId:cfg().userPoolClientId, Username:email.trim(), Password:password,
    UserAttributes:[{Name:'email',Value:email.trim()},{Name:'name',Value:name.trim()}] });
}
export async function confirmAccount(email,code) {
  if (isDemo()) return {preview:true};
  return cognito('ConfirmSignUp', { ClientId:cfg().userPoolClientId, Username:email.trim(),ConfirmationCode:code.trim() });
}
export async function resendConfirmation(email) {
  if (isDemo()) return {preview:true};
  return cognito('ResendConfirmationCode', {ClientId:cfg().userPoolClientId, Username:email.trim()});
}
export async function requestPasswordReset(email) {
  if (isDemo()) return {preview:true};
  return cognito('ForgotPassword', { ClientId:cfg().userPoolClientId, Username:email.trim() });
}
export async function completePasswordReset(email,code,password) {
  if (isDemo()) return {preview:true};
  return cognito('ConfirmForgotPassword', { ClientId:cfg().userPoolClientId,
    Username:email.trim(),ConfirmationCode:code.trim(),Password:password });
}
export async function signOut() {
  if (isDemo()) { sessionStorage.removeItem(DEMO_KEY); return; }
  // Local sign-out clears this browser tab. Access/refresh tokens aren't committed to code.
  sessionStorage.removeItem(SESSION_KEY);
}
