import assert from 'node:assert/strict';
import fs from 'node:fs';
const root=new URL('../',import.meta.url);
const read=(s)=>fs.readFileSync(new URL(s,root),'utf8');
const app=read('js/app.js'),css=read('css/style.css'),visuals=read('js/visuals.js');
const files=['index','browse','food-details','dashboard','add-food','my-listings','messages','profile','login','register','confirm-account','forgot-password','reset-password','how-it-works','privacy','faq'];
for(const x of files){const h=read(x+'.html');assert(h.includes('src="js/sharebite.bundle.js"'),x+' must use classic bundle');assert(!h.includes('type="module"'),x+' must not require browser modules');assert(h.includes('id="app"')&&h.includes('<main'),x+' must have fallback content');}
for(const field of ['foodName','category','description','quantity','location','expiryTime','allergyInfo','storageInstructions','preparedOn','pickupWindow','dietary','photo','photoGallery']){assert(app.includes('id="'+field+'"')||app.includes('name="'+field+'"'), 'Missing food field: '+field)}
for(const field of ['loginForm','registerForm','confirmForm','forgotForm','resetForm','messageDonorForm','threadSendForm','ratingForm'])assert(app.includes(field),'Missing interaction '+field);
for(const title of ['intro-skip','intro-ring','courier'])assert(app.includes(title),'Missing opening animation '+title);
assert(css.includes('prefers-reduced-motion'),'Accessibility: reduced-motion missing');
assert(css.includes('perspective:')&&css.includes('rotateY('),'3-D transforms missing');
assert(!/https:\/\/images\.unsplash\.com/.test(visuals),'Preview assets must be local, not external stock dependencies');
for(const slug of ['produce','bakery','meals','fruit','cafe','pantry'])assert(fs.existsSync(new URL('assets/food-'+slug+'.svg',root)),'Missing local food art '+slug);
assert(read('index.html').includes('Good food.')&&read('index.html').includes('assets/food-produce.svg'),'Index fallback is not complete');
console.log('PASS: 16 standalone pages, all food detail fields, account/messaging/rating forms, local images, accessible 3-D-style intro and fallback homepage.');
