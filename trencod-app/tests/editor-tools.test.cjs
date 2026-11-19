const test=require('node:test'),A=require('node:assert/strict'),W=require('../public/workspace.js');
test('literal search and replacement handle regex symbols, unicode and empty searches',()=>{
 A.deepEqual(W.matches('a.b aXb a.b','a.b'),[0,8]);
 A.deepEqual(W.matches('Score score','score'),[6]);
 A.deepEqual(W.matches('नमस्ते नमस्ते','नमस्ते'),[0,7]);
 A.deepEqual(W.matches('abc',''),[]);
 A.equal(W.replaceText('a.b a.b','a.b','$&'), '$& $&');
 A.equal(W.replaceText('score score','score','points',6),'score points');
 A.equal(W.replaceText('abc','','x'),'abc');
 A.throws(()=>W.replaceText('score','points','x',0),/Match changed/);
});
test('duplicate preserves folder, original text and save roundtrip; avoids collisions',()=>{
 const state={folders:['scripts'],files:[{path:'index.html',text:'<h1>Test</h1>'},{path:'scripts/main.py',text:'print("hello")'},{path:'scripts/main-copy.py',text:'old copy'}]};
 const copy=W.duplicate(state,'scripts/main.py');A.equal(copy.path,'scripts/main-copy-2.py');A.equal(state.files.length,3);A.equal(copy.state.files.at(-1).text,'print("hello")');
 A.deepEqual(W.load({html:W.compile(copy.state)}),copy.state);
 A.equal(W.duplicate(state,'index.html').path,'index-copy.html');
 A.throws(()=>W.duplicate(state,'missing.py'),/Select a file/);
});
test('oversized duplicates are rejected without modifying source',()=>{
 const state={folders:[],files:[{path:'index.html',text:'x'.repeat(50000)}]};
 A.throws(()=>W.duplicate(state,'index.html'),/too large/);A.equal(state.files.length,1);
});
