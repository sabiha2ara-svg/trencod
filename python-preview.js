'use strict';
// Python runs only inside an opaque-origin iframe worker, never on the app server.
function pythonPreview(state,active){
 const files=state.files.filter(f=>/\.py$/i.test(f.path));
 const data=JSON.stringify({files,active}).replace(/</g,'\\u003c');
 const worker=`onmessage=async e=>{try{
 importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js');
 const py=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.29.3/full/',stdout:s=>postMessage({text:s}),stderr:s=>postMessage({text:s})});
 py.setStdin({stdin:()=>{throw Error('Interactive input is not supported here. Set a variable in your code instead.');}});
 const {files,active}=e.data;for(const f of files){const p='/home/pyodide/'+f.path;py.FS.mkdirTree(p.slice(0,p.lastIndexOf('/')));py.FS.writeFile(p,f.text);}
 py.globals.set('_trencod_path','/home/pyodide/'+active);
 postMessage({ready:true});
 await py.runPythonAsync('import sys, os, runpy\\nsys.path.insert(0, os.path.dirname(_trencod_path))\\nrunpy.run_path(_trencod_path, run_name="__main__")');
 postMessage({done:true});
 }catch(e){postMessage({error:String(e.message||e)})}};`;
 return `<!doctype html><html><head><meta charset="utf-8"><style>body{background:#101524;color:#e9edff;font:15px/1.6 system-ui;margin:0;padding:20px}button{padding:9px 16px;border:1px solid #8e82b9;border-radius:9px;background:#292a47;color:white}pre{white-space:pre-wrap;overflow-wrap:anywhere}p{color:#b7bfdc}</style></head><body><h2>Python practice</h2><p id="state">Loading Python… First run needs an internet connection.</p><button id="stop">Stop Python</button><pre id="out" aria-live="polite"></pre><script>
 const out=document.getElementById('out'),status=document.getElementById('state');let worker,timer,url,used=0,ended=false;
 function finish(message){ended=true;clearTimeout(timer);worker?.terminate();if(url)URL.revokeObjectURL(url);status.textContent=message;document.getElementById('stop').disabled=true;}
 function append(text){const s=String(text)+'\\n';if(used+s.length>50000){finish('Output limit reached. Reduce print statements and run again.');return;}used+=s.length;out.textContent+=s;}
 document.getElementById('stop').onclick=()=>finish('Stopped. Edit your code and Run Python to start again.');
 try{url=URL.createObjectURL(new Blob([${JSON.stringify(worker).replace(/</g,'\\u003c')}],{type:'text/javascript'}));worker=new Worker(url);timer=setTimeout(()=>finish('Python took too long to load. Check your connection and try again.'),90000);
 worker.onmessage=e=>{if(ended)return;const m=e.data;if(m.ready){clearTimeout(timer);status.textContent='Running your Python code…';timer=setTimeout(()=>finish('Stopped after 15 seconds. Check for an endless loop.'),15000);}if(m.text!==undefined)append(m.text);if(m.error){append(m.error);finish('Python reported an error. Read the message and try a small fix.');}if(m.done)finish('Finished. Change something and try again.');};
 worker.onerror=e=>{append(e.message||'Runtime could not start.');finish('Python could not start in this browser. Your source can still be saved and downloaded.');};worker.postMessage(${data});
 }catch(e){append(e.message);finish('Python unavailable in this browser. Your source is still safe.');}
 window.addEventListener('pagehide',()=>finish('Stopped'));
 <\/script></body></html>`;
}
if(typeof module!=='undefined')module.exports=pythonPreview;
