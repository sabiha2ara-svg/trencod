const test=require('node:test'),A=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
let dom;try{dom=require('linkedom');}catch{}
test('saved art picker previews, inserts, filters and exported controls pause independently',{skip:!dom},async()=>{
 const {window}=dom.parseHTML('<html><body></body></html>'),document=window.document;
 Object.defineProperty(window.HTMLSelectElement.prototype,'value',{configurable:true,get(){return this._value??this.querySelector('option')?.value??''},set(v){this._value=v}});
 window.HTMLElement.prototype.showModal=function(){};window.HTMLElement.prototype.close=function(){this.dispatchEvent(new window.Event('close'))};window.HTMLCanvasElement.prototype.getContext=()=>({fillRect(){},set fillStyle(v){}});window.HTMLCanvasElement.prototype.toDataURL=()=> 'data:image/png;base64,AAAA';
 const body={frames:[Array(256).fill('#ffffff'),Array(256).fill('#000000')],fps:6};let inserted='';
 const c={window,document,user:{id:'test'},body,TextEncoder,TextDecoder,btoa,atob,console,api:async p=>p==='creations'?{creations:[{id:'123',name:'Dog walk',kind:'art',frame_count:2}]}:{file:{kind:'art',body}},toast:s=>{throw Error(s)},accept:s=>inserted=s};vm.createContext(c);
 for(const f of ['creator.js','workspace.js'])vm.runInContext(fs.readFileSync('public/'+f,'utf8'),c);
 await vm.runInContext('animationPicker(accept)',c);await new Promise(r=>setImmediate(r));
 const el=id=>document.querySelector('#'+id);A.match(el('anim-status').textContent,/Ready/);A.equal(el('anim-preview').getAttribute('sandbox'),'allow-scripts');
 el('anim-size').value='256';el('anim-speed').value='2';el('anim-flip').checked=true;el('anim-controls').checked=true;el('anim-size').oninput();A.match(el('anim-preview').srcdoc,/transform:scale\(2\)/);A.match(el('anim-preview').srcdoc,/scaleX\(-1\)/);
 el('anim-insert').onclick();A.equal(el('animation-picker'),null);A.match(inserted,/steps\(2\)/);c.markup=inserted;
 const source=vm.runInContext('insertAnimationHTML("<html><body><h1>Keep game</h1></BODY></html>",markup)',c);A.match(source,/<h1>Keep game<\/h1>/);c.state={folders:[],files:[{path:'index.html',text:source}]};const reopened=vm.runInContext('WorkspaceSource.load({html:WorkspaceSource.compile(state)})',c);A.equal(reopened.files[0].text,source);
 const {document:out}=dom.parseHTML(source),button=out.querySelector('.trencod-animation button'),sprite=out.querySelector('[role=img]');new Function(button.getAttribute('onclick')).call(button);A.equal(sprite.style.animationPlayState,'paused');new Function(button.getAttribute('onclick')).call(button);A.equal(sprite.style.animationPlayState,'running');
 A.throws(()=>vm.runInContext('animationEmbed(body,{size:999})',c),/size/);
 await vm.runInContext('animationPicker(accept)',c);await new Promise(r=>setImmediate(r));el('anim-search').value='missing';el('anim-search').oninput();A.equal(el('anim-insert').disabled,true);el('anim-close').onclick();A.equal(el('animation-picker'),null);
});
