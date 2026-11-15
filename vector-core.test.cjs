const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});vm.runInContext(fs.readFileSync('public/vector-core.js','utf8'),ctx);const sprites=vm.runInContext('vectorLibrary()',ctx);
assert.equal(sprites.length,50);assert.equal(new Set(sprites.map(s=>s.name)).size,50);
let drawn=0;const canvas=new Proxy({}, {get:()=>()=>{drawn++;},set:()=>true});
for(const s of sprites){const svg=ctx.vectorMarkup(s);assert(svg.startsWith('<svg'));assert(!/<script|<image|foreignObject|href=/i.test(svg));assert(s.shapes.length<=160);ctx.drawVectorSprite(canvas,{x:0,y:0,w:128,h:128},s);}
assert(drawn>1000);console.log('PASS 50 SVG exports and canvas draw paths');
