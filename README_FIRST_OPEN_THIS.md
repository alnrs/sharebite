# ShareBite 604AZ — ONE COMPLETE PROJECT · LIVE-CONFIGURED CANDIDATE

This folder contains **the full frontend and original-premium-backend source**. The browser configuration is **pre-filled with the public Outputs visible in the screenshot of the completed ShareBite 604AZ stack**. It is not evidence that real AWS sign-in, uploads, messaging, or CORS have passed yet: the two-account live acceptance test must still be performed in the user's lab.

**PLEASE KEEP YOUR WORKING CLOUDFORMATION STACK. DO NOT DELETE IT.** The supplied `infrastructure/ShareBite_604AZ_REVIEWED_CloudFormation.yaml` is a locally reviewed reference containing an important privacy correction, **not** something automatically applied to AWS.

## Step 1 — Unzip the whole project (Windows)

1. Download the one complete ZIP; in File Manager right-click it → **Extract All**.
2. Open the extracted folder. You should see `index.html`, `START_SHAREBITE_WINDOWS.bat`, `css/`, `js/`, `assets/`, `infrastructure/`, `tests/`, and `amplify.yml` directly together. Do not open/edit files inside the compressed ZIP.
3. Double-click `START_SHAREBITE_WINDOWS.bat`. With Python 3 installed, it opens **http://localhost:5500/index.html**. Keep the terminal window open. If Python is missing, use VS Code → File → Open Folder → choose this folder → right-click `index.html` → Open with Live Server (and pay attention to its origin and port).
4. From the **same** browser/origin, open **http://localhost:5500/connection-check.html** and click **Test public API health**. Do not open the HTML directly through `file://` to test live AWS functionality.
5. If the page is blank, read the browser Console (F12) and ensure `js/config.js`, `js/sharebite.bundle.js` and `css/style.css` all load (HTTP 200). This package uses no CDN for Cognito authentication.

### Cloud settings used

- Region: **us-east-1**
- API endpoint: your stack's public `ApiBaseUrl` ending in `/prod`, NOT `/prod/food`
- User pool ID / public client ID: copied from your AWS Outputs screenshot into `js/config.js`
- Mode: **live** by default, not simulated demo

If sign-in says the pool or client doesn't exist, verify the IDs in `js/config.js` *character by character* using the CloudFormation console Copy buttons. Do not replace them with AWS access keys. The public `/health` route should not require sign-in, but its browser CORS policy still depends on your actual `FrontendOrigin` setting.

## Step 2 — Read the actual AWS deployment procedure

**`DEPLOYMENT_GUIDE.md`** is the step-by-step path: Parameters → CORS → localhost checks → two-user acceptance test → Git Bash → new GitHub repo → AWS Amplify GitHub connection → `FrontendOrigin` update → retest. Follow it in that order.

`connection-check.html` identifies connection issues without requesting or displaying passwords or tokens. Python is used only to launch the frontend on your computer, not to host the final website.

## Everything inside this project

- **16 HTML pages**: homepage, browse, food details, dashboard, add-food, my listings, messages, profile, sign-in, registration, email confirmation, forgot password, reset password, how it works, privacy and FAQ.
- **Premium design**: editable CSS, local artwork, cinematic 3.7-second pseudo-3D introduction on first home visit, reduced-motion support, responsive layout.
- **Actual browser code**: `js/app.js`, `js/auth.js`, `js/api.js`, `js/visuals.js`, `js/demo-data.js`, `js/config.js`; `js/sharebite.bundle.js` is the generated browser-compatible bundle.
- **Authentication**: user-pool API requests for sign-up, confirmation, password sign-in, token refresh, forgot/reset password and tab-local sign-out. **No third-party CDN dependency**. JWT authorization is enforced by API Gateway, not by trusting browser state.
- **Listings**: food details, prepared/collection dates, allergies, storage, status changes by donor; camera/gallery inputs; private S3 presigned uploads.
- **Messaging**: authenticated donor-to-recipient inbox; no required public phone numbers. This is refresh-based text messaging, not WebSocket push chat.
- **Infrastructure**: reference reviewed CloudFormation YAML, matching Lambda and scheduled expiry source, structural verifier and backend tests. These **do not** modify your completed AWS stack.
- **Git + Amplify**: `amplify.yml` deploys **only the static website** from GitHub commits; backend sources stay outside the public hosting artifacts. `tools/create_amplify_zip.py` creates the alternate manual static upload ZIP.
- **Connection check**, `.gitignore`, launcher and tests.

## If you just want to inspect the design again without AWS

Run `python tools/set_mode.py demo`, then reopen the local homepage. This mode shows sample accounts/data/messages stored in your browser only. **Before deploying**, always run `python tools/set_mode.py live` and `npm run build` if you have changed JS source code. Amplify's `amplify.yml` also rebuilds the browser bundle and runs automated tests.

## Known constraints — important for your 604AZ evidence

- Public health endpoint not tested live from this offline workspace (external DNS is unavailable here). **Your lab is the final live test environment**.
- `FrontendOrigin` configured on YOUR STACK has not been shown. It must match the browser's exact origin, e.g. `http://localhost:5500` during local tests and the published HTTPS Amplify origin during hosting. The template currently allows one explicit origin at a time.
- The previously deployed template may use a Cognito email fallback as a public donor display name when a user profile lacks `name`. The reference reviewed template improves that fallback but isn't deployed automatically; don't use real personal data before reviewing this.
- Recipient-controlled reservations, real-time chat/push, message attachments, content moderation and editable profiles require future backend implementation. Do not represent them as completed in your report.
- Never push passwords, AWS access keys, user-token screenshots, or real user data into GitHub or chat.
