const test=require('node:test'),A=require('node:assert/strict'),vm=require('node:vm');
const W=require('../public/workspace.js'),preview=require('../public/python-preview.js');
const state={folders:['helpers'],files:[{path:'index.html',text:'<h1>Web game</h1>'},{path:'main.py',text:'print("</script>")'},{path:'helpers/math.py',text:'score = 5'}]};
test('Python source and icons survive save roundtrip without executing in HTML',()=>{
 A.deepEqual(W.load({html:W.compile(state)}),state);for(const [ext,type] of Object.entries({js:'JS',py:'PY',html:'HTML',css:'CSS'}))A.equal(W.fileType('folder/test.'+ext),type);
 const bad=structuredClone(state);bad.files[0].text='<script src="main.py"></script>';A.throws(()=>W.compile(bad),/Python practice/);
});
test('Practice iframe escapes source, worker runs selected path, Stop terminates',async()=>{
 const html=preview(state,'main.py');A.equal((html.match(/<\/script>/g)||[]).length,1);
 const code=html.match(/<script>([\s\S]*)<\/script>/)[1];let source,worker,posted,timeout;
 const elements={out:{textContent:''},state:{textContent:''},stop:{}};
 const c={document:{getElementById:id=>elements[id]},window:{addEventListener(){}},Blob:class{constructor(parts){source=parts[0]}},URL:{createObjectURL:()=> 'blob:test',revokeObjectURL(){}},Worker:class{constructor(){worker=this}postMessage(data){posted=data}terminate(){this.stopped=true}},setTimeout:(f)=>{timeout=f;return 1},clearTimeout(){}};
 vm.runInNewContext(code,c);A.deepEqual(JSON.parse(JSON.stringify(posted)),{files:state.files.slice(1),active:'main.py'});
 let run,paths=[],messages=[];const py={setStdin(){},FS:{mkdirTree(){},writeFile:(p,t)=>paths.push(p)},globals:{set(){}},runPythonAsync:async s=>{run=s}};
 const wc={importScripts(){},loadPyodide:async()=>py,postMessage:m=>messages.push(m)};vm.runInNewContext(source,wc);await wc.onmessage({data:posted});A.match(run,/runpy.run_path/);A.ok(paths.includes('/home/pyodide/helpers/math.py'));A.ok(messages.some(x=>x.done));
 worker.onmessage({data:{text:'My score: 5'}});A.match(elements.out.textContent,/My score: 5/);elements.stop.onclick();A.equal(worker.stopped,true);
});
