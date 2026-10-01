import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const base=new URL('../',import.meta.url);
const cfg=fs.readFileSync(new URL('js/config.js',base),'utf8').replace(/mode:\s*["']live["']/, "mode: \"demo\"");
const bundle=fs.readFileSync(new URL('js/sharebite.bundle.js',base),'utf8');
const pages=['home','browse','food-details','dashboard','add-food','my-listings','messages','profile','login','register','confirm-account','forgot-password','reset-password','how-it-works','privacy','faq'];
for(const page of pages){
  const local={};const sess={'sharebite-intro-seen':'1','sharebite604-demo-user':JSON.stringify({email:'demo@example.test',name:'Demo Member'})};
  const map=new Map();
  function element(id=''){if(!map.has(id)) map.set(id,{innerHTML:'',id,value:'',src:'',dataset:{},style:{},classList:{add(){},remove(){},toggle(){return true}},setAttribute(){},addEventListener(){},append(){},remove(){},querySelectorAll(){return []}});return map.get(id);}
  const doc={body:{dataset:{page},classList:{add(){},remove(){}},append(){},innerHTML:''},getElementById:element,querySelector(){return null},querySelectorAll(){return []},addEventListener(){},createElement:()=>element('el-'+Math.random())};
  const errors=[];
  const location={href:'http://localhost:5500/'+(page==='home'?'index':page)+'.html'+(page==='food-details'?'?id=demo-01':''),pathname:'/'+(page==='home'?'index':page)+'.html',search:page==='food-details'?'?id=demo-01':'',replace(s){errors.push('Unexpected redirect to '+s)}};
  const window={addEventListener(){},matchMedia:()=>({matches:true}),SHAREBITE_CONFIG:null};
  const ctx={window,document:doc,location,localStorage:{getItem:k=>local[k]||null,setItem:(k,v)=>{local[k]=v},removeItem:k=>delete local[k]},sessionStorage:{getItem:k=>sess[k]||null,setItem:(k,v)=>{sess[k]=v},removeItem:k=>delete sess[k]},matchMedia:()=>({matches:true}),URL,URLSearchParams,Date,Math,JSON,Object,Array,Map,Set,FormData,Blob,AbortSignal,console:{...console,error:(...e)=>errors.push(e.map(String).join(' '))},setTimeout:()=>0,clearTimeout(){},requestAnimationFrame:()=>1,cancelAnimationFrame(){},scrollY:0};
  vm.createContext(ctx);
  vm.runInContext(cfg,ctx,{timeout:2000});
  vm.runInContext(bundle,ctx,{timeout:4000});
  for(let i=0;i<15;i++)await Promise.resolve();
  let output=element('app').innerHTML;
  assert(output.includes('ShareBite'),page+' should render branded content');
  assert(!output.includes('Configuration check'),page+' threw an error: '+errors.join(' '));
  assert(!errors.length, page+' JS errors: '+errors.join(' '));
  console.log('BOOT PASS',page,output.length,'HTML characters');
}
