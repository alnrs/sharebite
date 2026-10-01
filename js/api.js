import {currentSession,isDemo} from './auth.js';
import {demo} from './demo-data.js';
const config=()=>window.SHAREBITE_CONFIG;
async function live(path,{method='GET',body,query}={}){
 const s=await currentSession();if(!s)throw Error('Please sign in to continue.');
 const c=config();const u=new URL(c.apiBaseUrl.replace(/\/+$/,'')+path);
 if(query)Object.entries(query).forEach(([k,v])=>{if(v!==undefined && v!==null && v!=='')u.searchParams.set(k,String(v));});
 const r=await fetch(u,{method,headers:{Authorization:'Bearer '+s.jwt,...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{}),signal:AbortSignal.timeout(20000)});
 let data;try{data=await r.json();}catch{data={message:'Unexpected server response. Check API URL and CloudWatch logs.'};}
 if(!r.ok)throw Error(data?.message||`API returned HTTP ${r.status}`);return data;
}
export async function health(){if(isDemo())return {status:'preview'};let u=new URL(config().apiBaseUrl.replace(/\/+$/,'')+'/health');let r=await fetch(u,{signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('Health check failed');return r.json();}
export async function getListings(){return isDemo()?demo.listings():live('/food');}
export async function getListing(id){return isDemo()?demo.one(id):live('/food/'+encodeURIComponent(id));}
export async function myListings(){return isDemo()?demo.mine():live('/my-food');}
export async function createListing(payload,photo){
 if(isDemo()){if(photo){if(photo.size>3*1024*1024)throw Error('For the local preview, use a photo smaller than 3 MB.');payload.imageUrl=await new Promise((resolve,reject)=>{let fr=new FileReader();fr.onload=()=>resolve(fr.result);fr.onerror=()=>reject(Error('Could not read photo'));fr.readAsDataURL(photo)});}return demo.add(payload,'demo-user',(await currentSession()).claims.name);}
 let body={...payload};if(photo){const signed=await live('/uploads/presign',{method:'POST',body:{contentType:photo.type,size:photo.size}});const form=new FormData();Object.entries(signed.fields).forEach(([k,v])=>form.append(k,v));form.append('file',photo);const upload=await fetch(signed.uploadUrl,{method:'POST',body:form,mode:'cors'});
 if(!upload.ok)throw Error('Photo upload failed. Check your S3 CORS FrontendOrigin setting.');body.imageKey=signed.imageKey;
 }return live('/food',{method:'POST',body});
}
export async function updateListing(id,status){return isDemo()?demo.update(id,status):live('/food/'+encodeURIComponent(id),{method:'PATCH',body:{status}});}
export async function getInbox(){return isDemo()?demo.inbox():live('/conversations');}
export async function getThread(id){return isDemo()?demo.messages(id):live('/messages',{query:{threadId:id}});}
export async function sendMessage(data){return isDemo()?demo.send(data.listingId,data.toUserId,data.text):live('/messages',{method:'POST',body:data});}
export async function getRating(id){return isDemo()?demo.rating(id):live('/ratings',{query:{listingId:id}});}
export async function addRating(id,score){return isDemo()?demo.rate(id,score):live('/ratings',{method:'POST',body:{listingId:id,score}});}
export async function getProfile(){return isDemo()?{userId:'demo-user',name:(await currentSession())?.claims.name,email:(await currentSession())?.claims.email}:live('/me');}
