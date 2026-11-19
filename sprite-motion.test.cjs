const test=require('node:test'),A=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
test('chase, patrol, follow and still movement preserve role and costume',()=>{
 const text=fs.readFileSync('public/visual-runtime.js','utf8'),c={};vm.createContext(c);vm.runInContext(text.slice(text.indexOf('function moveActor(')),c);
 for(const movement of ['chase','patrol','follow','still']){const a={x:100,y:100,w:32,h:32,originX:100,direction:1,type:'pet',sprite:'dog'};c.moveActor(a,movement,100,.1,{x:200,y:200});A.equal(a.type,'pet');A.equal(a.sprite,'dog');if(movement==='still')A.equal(a.x,100);else A.ok(a.x>100);if(movement==='follow')A.ok(a.y>100);}
 const a={x:175,y:0,w:32,h:32,originX:100,direction:1};c.moveActor(a,'patrol',100,.1,{x:0,y:0});A.equal(a.x,180);A.equal(a.direction,-1);c.moveActor(a,'patrol',100,.1,{x:0,y:0});A.equal(a.x,170);
});
