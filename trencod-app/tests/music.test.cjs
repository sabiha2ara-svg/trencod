const A=require('node:assert/strict'),test=require('node:test');global.location={origin:'https://trencod.example'};
const M=require('../public/music.js'),W=require('../public/workspace.js');
const m={id:'ab'.repeat(12),volume:.25,loop:true};
test('music survives compiled source save, reopen, replacement and removal',()=>{
 const html=M.insert('<html><body><h1>Game</h1></body></html>',m);A.deepEqual(M.read(html),m);A.match(html,/https:\/\/trencod.example\/media\/music\//);A.match(html,/<audio controls/);A.doesNotMatch(html,/autoplay/);
 const source={folders:[],files:[{path:'index.html',text:html}]};const compiled=W.compile(source);const reopened=W.load({html:compiled});A.deepEqual(M.read(reopened.files[0].text),m);
 const updated=M.insert(html,{...m,volume:0,loop:false});A.equal((updated.match(/<audio /g)||[]).length,1);A.equal(M.read(updated).volume,0);A.doesNotMatch(M.insert(updated,null),/<audio /);A.match(M.insert(updated,null),/<h1>Game/);
});
test('music refuses invalid IDs and settings',()=>{
 for(const value of [{...m,id:'" onerror="bad'},{...m,volume:NaN},{...m,volume:2},{...m,loop:'true'}])A.throws(()=>M.clean(value));
 A.equal(M.read('<!--trencod-music:bad--><!--/trencod-music-->'),null);
});
