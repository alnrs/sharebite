export const icons = {
  arrow: '<path d="M5 12h14m-6-6 6 6-6 6"/>',
  arrowUp: '<path d="M7 17 17 7M8 7h9v9"/>',
  chevron:'<path d="m9 18 6-6-6-6"/>',
  leaf:'<path d="M11 20A7 7 0 0 1 3 12C3 6 12 3 21 3c0 9-3 18-9 18ZM4 21c4-9 9-11 13-13"/>',
  heart:'<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0l-1 1-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  map:'<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
  calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  bag:'<path d="M5 8h14l1 13H4L5 8ZM9 9V6a3 3 0 0 1 6 0v3"/>',
  camera:'<path d="M4 7h4l2-3h4l2 3h4v13H4V7Z"/><circle cx="12" cy="13" r="3"/>',
  user:'<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  users:'<circle cx="9" cy="8" r="3"/><path d="M3 19a6 6 0 0 1 12 0M18 11a3 3 0 0 0-1-6M18 19h3a5 5 0 0 0-5-5"/>',
  message:'<path d="M20 17a3 3 0 0 1-3 3H6l-4 2V7a4 4 0 0 1 4-4h11a4 4 0 0 1 4 4v10Z"/>',
  shield:'<path d="M12 2 21 6v6c0 6-4 9-9 10C7 21 3 18 3 12V6l9-4Z"/><path d="m8 12 3 3 5-6"/>',
  check:'<path d="m5 12 5 5 9-10"/>',
  checkCircle:'<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
  sliders:'<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="9" cy="18" r="2"/>',
  grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  star:'<path d="m12 2 3 6 7 .9-5 4.7 1.3 6.8L12 17l-6.3 3.4L7 13.6 2 9l7-.9 3-6Z"/>',
  upload:'<path d="M12 17V3m-5 5 5-5 5 5M4 17v3h16v-3"/>',
  spark:'<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5L12 2Z"/>',
  menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
  close:'<path d="m5 5 14 14M19 5 5 19"/>',
  logout:'<path d="M10 17l5-5-5-5M15 12H3M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/>',
  alert:'<path d="M12 3 2 21h20L12 3ZM12 9v5M12 18h.01"/>',
  mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
  plus:'<path d="M12 5v14M5 12h14"/>',
  back:'<path d="m15 18-6-6 6-6"/>',
  food:'<path d="M3 12c0 7 4 10 9 10s9-3 9-10H3ZM7 3v5M12 2v6M17 3v5"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4 4l1.5 1.5m13 13L20 20M2 12h2m16 0h2M4 20l1.5-1.5m13-13L20 4"/>',
};
export function icon(name, size=20, cls='') {return `<svg class="icon ${cls}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]||icons.spark}</svg>`;}
export function escapeHTML(value='') {return String(value ?? '').replace(/[&<>"']/g, ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
export function safeImage(url) { if(!url) return 'assets/food-fallback.svg'; try { if (/^assets\/food-(?:produce|bakery|meals|fruit|cafe|pantry|fallback)\.svg$/.test(String(url))) return String(url); if (window.SHAREBITE_CONFIG?.mode==='demo' && /^data:image\/(?:jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(String(url))) return String(url); const u = new URL(url, location.href); return ['https:','http:'].includes(u.protocol) ? escapeHTML(u.href) : 'assets/food-fallback.svg'; } catch {return 'assets/food-fallback.svg';}}
export const demoPhotos = {
  produce:'assets/food-produce.svg',
  bakery:'assets/food-bakery.svg',
  meals:'assets/food-meals.svg',
  fruit:'assets/food-fruit.svg',
  cafe:'assets/food-cafe.svg',
  pantry:'assets/food-pantry.svg'
};
export function fmtTime(x){try{return new Date(x).toLocaleString('en-GB',{day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});}catch{return x||'Flexible';}}
export function fmtDay(x){try{return new Date(x).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});}catch{return 'Not specified';}}
export function timeLeft(x){let hrs=(new Date(x).getTime()-Date.now())/3.6e6; if(!Number.isFinite(hrs))return 'Flexible';if(hrs<0)return 'Past collection time';if(hrs<1)return 'Under an hour left';if(hrs<24)return `${Math.ceil(hrs)} hours left`;return `${Math.ceil(hrs/24)} days left`;}
export function extraDescription(text){ // Extra frontend fields are preserved inside the backend's supported description field.
  const [base,extra] = String(text||'').split('\n\n--- Pickup details ---\n'); const obj={description:base};
  if(extra)extra.split('\n').forEach(line=>{let n=line.indexOf(':');if(n>0)obj[line.slice(0,n).trim()]=line.slice(n+1).trim();}); return obj;
}
export function logo(white=false){return `<span class="brand-icon ${white?'brand-icon--white':''}">${icon('leaf',21)}</span><span class="brand-word">Share<span>Bite</span><small class="brand-point">.</small></span>`;}
