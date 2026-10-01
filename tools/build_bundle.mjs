// Dependency-free bundle generation for Amplify's Node.js build environment.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const js=path.join(here,'..','js');
const filenames=['visuals.js','demo-data.js','auth.js','api.js','app.js'];
const sections=filenames.map(filename=>{
  let source=fs.readFileSync(path.join(js,filename),'utf8');
  source=source.replace(/^import\s+\{[^}]+\}\s+from\s+['"][^'"]+['"];\s*/gm,'');
  source=source.replace(/\bexport\s+(?=(?:const|let|var|function|async function|class)\b)/g,'');
  if(filename==='app.js')source='const e=escapeHTML, img=safeImage;\n'+source;
  return `// === ${filename} ===\n${source}`;
});
const out='/* ShareBite single classic browser bundle. Generated from js source. */\n(function(){"use strict";\n'+sections.join('\n')+'\n})();\n';
fs.writeFileSync(path.join(js,'sharebite.bundle.js'),out);
console.log(`Built js/sharebite.bundle.js (${out.length} bytes)`);
