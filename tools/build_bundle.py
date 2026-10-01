from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/'js'
sources=[]
for filename in ['visuals.js','demo-data.js','auth.js','api.js','app.js']:
 text=(root/filename).read_text()
 text=re.sub(r"^import\s+\{[^}]+\}\s+from\s+['\"][^'\"]+['\"];\s*",'',text,flags=re.M)
 text=re.sub(r'\bexport\s+(?=(?:const|let|var|function|async function|class)\b)','',text)
 if filename=='app.js':text='const e=escapeHTML, img=safeImage;\n'+text
 sources.append('// ═══ '+filename+' ═══\n'+text)
bundle='/* ShareBite Studio offline-compatible classic bundle. Generated; edit component source files instead. */\n(function(){"use strict";\n'+ '\n'.join(sources)+'\n})();\n'
(root/'sharebite.bundle.js').write_text(bundle)
print('Built bundle:',root/'sharebite.bundle.js',len(bundle),'bytes')
