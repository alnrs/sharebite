# ShareBite 604AZ — From completed CloudFormation to live Amplify website

This is a **staged deployment**, not an automatic all-in-one Git/Amplify integration. Your `ShareBite-604AZ-Premium-Cloud-Infrastructure` stack showed **CREATE_COMPLETE** in `us-east-1` and published the required API/Cognito Outputs. The frontend here is preconfigured with those *public* values. **Do not share any AWS keys, passwords, Cognito session tokens or Secrets Manager contents.**

## Phase A: Confirm the current stack — do not delete it

1. AWS console → N. Virginia (`us-east-1`) → CloudFormation → Stacks → `ShareBite-604AZ-Premium-Cloud-Infrastructure`. Confirm **CREATE_COMPLETE**.
2. **Outputs**: verify `ApiBaseUrl`, `CognitoUserPoolId`, `CognitoAppClientId`, and `Region` in `js/config.js`. The app uses `ApiBaseUrl` **ending `/prod`**; the frontend API code adds `/food` and the other endpoints automatically.
3. **Parameters** tab: look up **FrontendOrigin**. If `http://localhost:5500`, leave it for the local test. If different, either use the exact configured browser origin or update the SAME stack's `FrontendOrigin` parameter through a REVIEWED CHANGE SET. Keep every other stack setting unchanged. **CORS is required for both API Gateway and the private photo bucket.** Avoid wildcard origins for this prototype.
4. **Resources** tab: confirm your stack includes the API, Lambda, Cognito user pool/client, listings/messages/conversations/ratings tables and private S3 bucket. Optional Amplify scaffolding is **not** automatically connected to GitHub. Do not create a duplicate CloudFormation stack for your website.

## Phase B: Open the complete project from File Manager

1. Extract ALL files from this ZIP into one normal folder. `index.html`, `js`, `css`, `assets`, `infrastructure` and `amplify.yml` are at the same project root.
2. Double-click `START_SHAREBITE_WINDOWS.bat` (requires Python 3), or open the entire extracted folder in VS Code and open `index.html` via Live Server. **`file://` pages are not suitable for AWS tests**.
3. Use exactly `http://localhost:5500` for the local browser origin if this matches your CloudFormation parameter. If the port is occupied, close the other server first or update your allowed origin to the actual port used.
4. Open `http://localhost:5500/connection-check.html`. Click **Test public API health**. Expected response from the configured backend is `{"status":"ok",...}`. If you see CORS in DevTools Console, compare your browser's exact `location.origin` with the CloudFormation **FrontendOrigin** parameter. If HTTP 403/404, compare `ApiBaseUrl` with the screenshot's **ApiBaseUrl**, not **FoodApiUrl**. Record the actual test result.

## Phase C: Validate REAL accounts and backend behavior

**Use test data and disposable photographs only. Do not onboard real food donors until privacy/safety work is complete.**

1. `register.html`: register donor TEST A using a new email in the NEW Cognito pool and a 12+ character password with uppercase, lowercase, digits and symbol. Complete the code in `confirm-account.html`. Your old AWS lab accounts will not appear in the new user pool.
2. `login.html`: sign in; then refresh `dashboard.html`. From another browser profile/incognito session register and confirm recipient TEST B.
3. Test `forgot-password.html` and `reset-password.html` (on a test account). Don't share recovery codes.
4. Donor A: create a listing with general collection area (not full home address), food name, quantity, expiry, storage and allergens; select a small JPG, PNG or WebP (max 5 MB). Verify API create and private S3 upload and then check `my-listings.html`.
5. Recipient B: sign in; browse, open A's listing, choose **Message donor**, and send a sample message. From donor A's browser profile, check the inbox, reply, then refresh B's inbox. Messaging is authenticated *poll/refresh text communication*, not WebSocket live chat. Do not exchange phone numbers in test messages.
6. Verify recipient B can't edit A's listing or open a conversation they don't belong to. Test donor status updates and ratings. Inspect API Gateway response codes and CloudWatch Lambda logs if anything fails.
7. The backend deployed in the old premium template can expose a donor's verified email as the public donor name if `name` was absent. The reviewed copy in `infrastructure/` fixes the fallback for newly created listings, **but your deployed stack isn't automatically updated**. Do not use real personal information until a reviewed update and review of any existing test data.

**If the test fails:** F12 browser DevTools → Console and Network; note whether it was a Cognito request (`cognito-idp.us-east-1.amazonaws.com`), API request (`execute-api.../prod`), or private S3 upload. Share only the HTTP status/error text and a redacted screenshot, never headers or tokens.

## Phase D: Create your new GitHub repo and push THIS FOLDER with Git Bash

GitHub and Amplify are NOT automatically connected by CloudFormation. You must authorize the Amplify GitHub app or use manual upload. The repository can be private if desired; avoid adding real user data, AWS credentials or .env files.

1. Go to GitHub → New repository → choose a new name, such as **ShareBite-604AZ**; choose Public/Private appropriately. Leave it empty initially (do not initialize README/gitignore on the website because those files are already here). Copy YOUR new repository URL.
2. Open Git Bash *inside the extracted complete project folder* (the folder containing `index.html` and `amplify.yml`). Paste these one line at a time:

```bash
git init
git branch -M main
git status
git add .
git status
git commit -m "ShareBite 604AZ frontend and infrastructure source"
git remote add origin https://github.com/YOUR-USERNAME/YOUR-NEW-REPO.git
git push -u origin main
```

If you already initialized a Git repository, **do not run `git init` again**; check `git remote -v` first. Replace the example remote with your actual repository URL. GitHub may open a browser to authorize Git. Review `git status` before committing to ensure you aren't including credentials or screenshots with private data. The project `.gitignore` excludes keys, `.env`, ZIP archives, Python caches and build output.

## Phase E: Connect GitHub to AWS Amplify Hosting

1. In AWS Console (N. Virginia), open **AWS Amplify**. If your stack's optional empty Amplify scaffold was enabled, its app may already exist but **it is not connected**. Otherwise choose **Create new app / Host web app**.
2. Select **GitHub** as the source. Follow the GitHub authorization prompt; authorize the appropriate repository. Choose your new ShareBite repository and the **main** branch. If AWS Academy prohibits GitHub integration, see Phase F instead.
3. Amplify should detect `amplify.yml` in the repository root. Verify these key settings: `frontend` build runs `npm run build`, then `npm test`, and deploy artifact directory is **dist**. The build copies only the HTML/CSS/artwork/public `js/config.js` and generated JS bundle; backend sources do not appear on the public site.
4. Save/deploy. Wait for the Amplify **build/deploy job** to report success. Copy the final HTTPS web origin shown in Amplify, e.g. `https://main.XXXXXXXX.amplifyapp.com` (**your actual value will differ**). The first site build can render the design while authenticated API calls fail CORS until Phase G.

AWS docs: [Amplify GitHub setup](https://docs.aws.amazon.com/amplify/latest/userguide/setting-up-GitHub-access.html) and [Amplify build specification](https://docs.aws.amazon.com/amplify/latest/userguide/yml-specification-syntax.html).

## Phase F (alternative): Host without GitHub if your lab restricts authorization

From your extracted project folder, keep mode **live** and run `python tools/create_amplify_zip.py`. This generates `ShareBite_Amplify_UPLOAD.zip`, containing `index.html` at its ZIP ROOT with only public website assets. In Amplify, create a static app for **manual deployment** and upload **that static ZIP**, not the complete project ZIP. GitHub automatic redeployments are not available under manual hosting until a repository is connected separately.

## Phase G: Allow your final Amplify HTTPS website to use the SAME AWS backend

The template currently uses ONE explicit allowed `FrontendOrigin` for **API Gateway and S3 CORS**. A new Amplify domain is different from local `http://localhost:5500`.

1. Return to CloudFormation → the SAME successful ShareBite stack → **Update**. Choose **Use current template** and **keep all existing parameter values**, changing ONLY `FrontendOrigin` to your newly published Amplify HTTPS **origin** (scheme + host, NO slash/path at the end).
2. If your console supports it, create a **change set**, check the exact resource changes, and execute only after verifying that no unexpected deletions/replacements will occur. If IAM permissions reject the update, stop and inspect Events rather than deleting the successful stack.
3. Wait for **UPDATE_COMPLETE**. This updates the permitted cross-origin address for API Gateway and the private photograph bucket. Because there's only one allowed origin in the current template, your localhost API requests may then be blocked by CORS until that origin is restored or a future multi-origin template is designed.
4. At your **HTTPS Amplify website**, open `/connection-check.html` and run public health, then REPEAT the real donor/recipient account tests, password reset, photo upload, conversations and data-permission checks. Take redacted screenshots for 604AZ evidence.

## Future GitHub updates after you connect Amplify

Edit JS source or CSS in VS Code; run `npm run build` and `npm test` locally if Node is installed. Then Git Bash:

```bash
git add .
git commit -m "Improve ShareBite frontend"
git push origin main
```

Amplify connected to GitHub will then automatically build and deploy changes from your branch if automatic builds are enabled in Amplify. For deployment issues inspect the Amplify **Build** logs; for backend errors inspect CloudWatch; for CORS errors inspect the browser's Network/Console.

## Safety/limitations

This is a university prototype, not a public health/food-safety-certified service. It still needs real-user testing, data-protection checks, moderation, expiry/collection rules, monitoring and production threat review. Recipient-driven reservations, true real-time chat and editable profiles are future backend work. The **public `/health` test doesn't establish working authentication or message delivery**. Do not claim full production readiness in your report.
