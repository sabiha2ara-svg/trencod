const test=require('node:test'),A=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
test('areas append ground, move goal, preserve costumes and enforce limit',()=>{
 const source=fs.readFileSync('public/adventures.js','utf8');const c={structuredClone};vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function expandSceneArea'),source.indexOf('function defaultScene')),c);
 const initial={objects:[{type:'player',x:50,y:0,w:24,h:32},{type:'goal',x:740,y:370,w:30,h:50},{type:'platform',x:0,y:420,w:800,h:30,sprite:'grass'}]};
 let s=c.expandSceneArea(initial);A.equal(s.world_width,1600);A.equal(s.objects.at(-1).x,800);A.equal(s.objects.at(-1).sprite,'grass');A.equal(s.objects[1].x,1540);A.equal(initial.objects[1].x,740);
 for(let i=0;i<3;i++)s=c.expandSceneArea(s);A.equal(s.world_width,4000);A.throws(()=>c.expandSceneArea(s),/Maximum 5/);
});
function runtime(scene){
 const elements=new Map(),translations=[];const ctx=new Proxy({translate:(x,y)=>translations.push([x,y])},{get:(o,k)=>o[k]??(()=>{})});
 const doc={querySelector:s=>{if(!elements.has(s))elements.set(s,s==='#game'?{getContext:()=>ctx}:{});return elements.get(s);}};
 const c={scene,document:doc,window:{addEventListener(){}},performance:{now:()=>0},requestAnimationFrame(){}};vm.createContext(c);
 let source=fs.readFileSync('public/visual-runtime.js','utf8');source=source.replace('reset();requestAnimationFrame(frame);','reset();globalThis.check={step,render,reset,state:()=>({player,solids,dead,won}),press};');vm.runInContext(source,c);return {api:c.check,translations};
}
test('moving platform carries player, reverses and resets without mutating saved scene',()=>{
 const scene={speed:220,jump:450,gravity:950,objects:[{type:'player',x:120,y:268,w:24,h:32},{type:'platform',x:100,y:300,w:150,h:24,movement:'patrol',move_speed:80,sprite:'original'},{type:'goal',x:740,y:370,w:30,h:50}]};
 const {api}=runtime(scene);api.step(.025);const first=api.state().player.x;for(let i=0;i<20;i++)api.step(.025);A.ok(api.state().player.x>first+30);A.equal(api.state().player.y,268);A.equal(api.state().solids[0].sprite,'original');
 for(let i=0;i<25;i++)api.step(.025);A.equal(api.state().solids[0].direction,-1);A.equal(scene.objects[1].x,100);
 api.press('jump');api.step(.025);A.ok(api.state().player.y<268);api.reset();A.equal(api.state().solids[0].x,100);
});
test('player crosses into new area and camera follows',()=>{
 const scene={world_width:1600,speed:220,jump:450,gravity:950,objects:[{type:'player',x:760,y:388,w:24,h:32},{type:'platform',x:0,y:420,w:800,h:30},{type:'platform',x:800,y:420,w:800,h:30},{type:'goal',x:1540,y:370,w:30,h:50}]};
 const {api,translations}=runtime(scene);api.press('right');for(let i=0;i<40;i++)api.step(.025);A.ok(api.state().player.x>900);A.equal(api.state().dead,false);api.render();A.ok(translations.at(-1)[0]<-400);
});
