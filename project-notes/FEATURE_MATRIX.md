# ShareBite detailed feature audit

Status language: **Frontend** means browser code exists; **Backend** means the *reviewed template*
implements the route/service; **AWS verified?** remains **NO** until tested against the new lab.

| Requested feature | Frontend | Reviewed backend | Notes / limits |
| --- | --- | --- | --- |
| Premium home and animated entrance | Yes | Not needed | ~3.7 s CSS/SVG pseudo-3D scene, once/tab, skip/reduced motion. This is **not** a full 3D game-engine animation. |
| Responsive dashboard, accessibility | Yes | Partial | Test in real browsers and on phones after config. |
| Email registration / confirmation | Yes | Cognito pool/client | Registration requires an email you can verify. |
| Secure sign-in / sign-out | Yes | Cognito JWT authorizer | New lab users must register again. |
| Forgot and reset password | Yes | Cognito verified-email recovery | Requires SDK access/network and confirmed email. |
| Food categories/search/filter/details | Yes | GET food API | Live GET `/food` requires sign-in; search filters client side for current 40 listings. |
| Add food, quantity, expiry, location, allergies, storage | Yes | POST food API | Timezone-aware UTC expiry sent by frontend. |
| Date food prepared / pickup window / dietary notes | Yes | Stored in description text | UI handles fields; database does not have separate typed indexes for them. |
| Take camera photo or select from device | Yes | Private S3 presigned POST | Browser camera permission & upload CORS must be tested live. JPG/PNG/WebP 5 MB max. |
| Donor/recipient private text messages without public phone numbers | Yes | Conversations + messages DynamoDB | Inbox refresh; **not real-time WebSocket** or message push. |
| Listing rating | Yes | Ratings DynamoDB | One rating/user/listing; **not proof of collection** and should not be marketed as verified feedback. |
| Donor's own listings + status changes | Yes | Owner-scoped endpoints | Donor can mark available/reserved/collected/removed. |
| Recipient-initiated reservation workflow | No | No | Needs reservation API with ownership, atomic capacity/availability and confirmation rules. |
| View own profile | Yes | JWT /me | **Read-only**. Profile editing requires separate backend/Cognito support. |
| SNS notifications | Limited | Generic backend SNS publish | Actual email delivery requires approved/confirmed SNS subscription; not in-app push. |
| EventBridge expiry and advanced monitoring | N/A | Optional stack switches | Not claimable as deployed until verified in new stack Resources. |
| CloudFront / WAF / AWS Backup | N/A | Optional, lab-dependent | CloudFront WAF protects static website only if enabled. |
| Amplify Hosting | Static site compatible | Optional empty app scaffold | User must publish manually or link newly created GitHub repository. |

Demo mode uses **local browser sample data only**. Demo logins accept arbitrary values and are
**not secure authentication**, and demo messages are not actually shared between browsers.
Live mode uses Cognito and signed API requests and requires a functioning new AWS deployment.
