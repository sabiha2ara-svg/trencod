const test=require('node:test'),A=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{parseHTML}=require('linkedom');
test('late shared save cannot overwrite a newly opened file identity',async()=>{
 const {window}=parseHTML('<main id="app"></main>'),document=window.document;
 const room={room:{name:'Team',owner:'a',invite:'private'},members:[],messages:[],files:[]};let resolveSave,lastPayload;
 const c={window,document,app:document.querySelector('#app'),$:s=>document.querySelector(s),user:{id:'a'},routeVersion:1,dirty:false,esc:String,confirm:()=>true,api:async(path,data)=>{if(path==='files'){lastPayload=data;return new Promise(r=>resolveSave=r);}return room;},setInterval:()=>1,clearInterval(){},toast(){},location:{},console};vm.createContext(c);vm.runInContext(fs.readFileSync('public/creator.js','utf8'),c);await vm.runInContext('creatorHub("room",1)',c);
 c.$('#new-code').onclick();c.$('#shared-html').value='first';const pending=c.$('#save-shared').onclick();c.$('#new-code').onclick();c.$('#shared-html').value='second';resolveSave({id:'first-id',revision:1});await pending;
 A.equal(vm.runInContext('sharedCode.id',c),null);A.equal(c.$('#shared-html').value,'second');A.match(c.$('#shared-state').textContent,/New shared file/);
 const second=c.$('#save-shared').onclick();A.equal(lastPayload.id,null);A.equal(lastPayload.body.html,'second');resolveSave({id:'second-id',revision:1});await second;A.equal(vm.runInContext('sharedCode.id',c),'second-id');
});
