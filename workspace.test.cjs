const A=require('node:assert/strict'),W=require('../public/workspace.js');
const base=()=>({folders:['styles','scripts'],files:[{path:'index.html',text:'<h1>Doggy 🐶</h1><link rel="stylesheet" href="styles/a.css"><script src="scripts/main.js"></script>'},{path:'styles/a.css',text:'@import "b.css"; body{color:red}'},{path:'styles/b.css',text:'h1{font-size:24px}'},{path:'scripts/main.js',text:'window.gameStarted=true;'}]});
let n=0;function test(name,f){f();n++;console.log('PASS '+name)}
test('Unicode source round trip and nested CSS',()=>{let w=base(),h=W.compile(w);A.deepEqual(W.load({html:h}),w);A.match(h,/<style>h1\{font-size/);A.match(h,/<script>window.gameStarted/)});
test('Legacy migration',()=>{let h=W.compile(W.load({html:'<h1>Hi</h1>',css:'body{margin:0}',js:'alert(1)'}));A.match(h,/body\{margin:0\}/);A.match(h,/alert\(1\)/)});
test('Missing file',()=>{let w=base();w.files.pop();A.throws(()=>W.compile(w),/Missing file/)});
test('CSS cycle',()=>{let w=base();w.files[2].text='@import "a.css";';A.throws(()=>W.compile(w),/Circular/)});
test('Unsafe and duplicate paths',()=>{for(let path of ['../evil.js','/bad.js','a//b.js','index.html']){let w=base();w.files.push({path,text:''});A.throws(()=>W.validate(w))}});
test('Entry required',()=>A.throws(()=>W.validate({files:[],folders:[]}),/index.html/));
test('Modules explain unsupported behavior',()=>{let w=base();w.files[3].text='import x from "./x.js"';A.throws(()=>W.compile(w),/module imports/)});
test('Script closing tag escaping',()=>{let w=base();w.files[3].text='let s="</script>";';A.ok(W.compile(w).includes('let s="<\\/script>"'))});
test('External URLs preserved',()=>{let w=base();w.files[0].text='<img src="https://example.com/a.png">';A.match(W.compile(w),/https:\/\/example.com\/a.png/)});
test('Size limit',()=>{let w=base();w.files[0].text='x'.repeat(90001);A.throws(()=>W.compile(w),/too large/)});
console.log(n+' passed');
test('Required sale credit retained when reopening sources',()=>{const h=W.compile(base())+'<footer>Original creator: @Maker</footer>';A.match(W.compile(W.load({html:h})),/<footer>Original creator: @Maker<\/footer>/)});
