function drawSceneBackground(ctx,bg={}){
 const palettes={night:['#14233f','#263a5c','#334c70'],meadow:['#c9eaf5','#91cda4','#6fae86'],desert:['#f5dca8','#d8b17f','#ba8d67'],snow:['#c9dfea','#e5f0f5','#b4cedc'],sunset:['#ecc1b2','#c899ad','#8a7f9e'],space:['#151d35','#343257','#595078']},p=palettes[bg.theme]||palettes.night;
 ctx.fillStyle=bg.color||p[0];ctx.fillRect(0,0,800,450);
 if(bg.theme==='solid')return;
 ctx.fillStyle=p[1];for(let i=0;i<7;i++){ctx.beginPath();ctx.arc(i*140,430,170,Math.PI,Math.PI*2);ctx.fill();}
 ctx.fillStyle=p[2];for(let i=0;i<6;i++){ctx.beginPath();ctx.arc(i*170+50,490,160,Math.PI,Math.PI*2);ctx.fill();}
 ctx.fillStyle=bg.theme==='night'||bg.theme==='space'?'#e2dcad':'#fff1c7';ctx.beginPath();ctx.arc(670,80,32,0,Math.PI*2);ctx.fill();
 if(bg.theme==='space')for(let i=0;i<36;i++)ctx.fillRect((i*127)%800,(i*59)%280,2,2);
}
function drawSpritePixels(ctx,o,art,time){if(art.type==='vector'){drawVectorSprite(ctx,o,art);return;}const frame=art.frames[Math.floor(time/1000*art.fps)%art.frames.length];for(let i=0;i<256;i++)if(frame[i]){ctx.fillStyle=frame[i];const x=Math.round(o.x+(i%16)*o.w/16),y=Math.round(o.y+Math.floor(i/16)*o.h/16);ctx.fillRect(x,y,Math.ceil(o.w/16),Math.ceil(o.h/16));}}
(()=>{
 const canvas=document.querySelector('#game'),ctx=canvas.getContext('2d'),status=document.querySelector('#game-status'),keys=new Set();
 const solids=scene.objects.filter(o=>o.type==='platform'),spawn=scene.objects.find(o=>o.type==='player'),goal=scene.objects.find(o=>o.type==='goal');
 let player,coins,enemies,pets,decorations,won=false,dead=false,jumpQueued=false,last=0;
 const hit=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
 function reset(){player={...spawn,vx:0,vy:0,ground:false};coins=scene.objects.filter(o=>o.type==='coin').map(o=>({...o,taken:false}));enemies=scene.objects.filter(o=>o.type==='enemy').map(o=>({...o,originX:o.x,direction:1}));pets=scene.objects.filter(o=>o.type==='pet').map(o=>({...o}));decorations=scene.objects.filter(o=>o.type==='decoration').map(o=>({...o,originX:o.x,direction:1}));won=dead=false;keys.clear();jumpQueued=false;status.textContent='Collect all coins, avoid enemies, then reach the flag.';}
 function press(k){if(k==='jump')jumpQueued=true;else keys.add(k);}
 for(const [id,key] of [['left','left'],['right','right'],['jump','jump']]){const b=document.querySelector('#'+id);b.onpointerdown=e=>{e.preventDefault();b.setPointerCapture(e.pointerId);press(key);};b.onpointerup=b.onpointercancel=()=>keys.delete(key);}
 document.querySelector('#reset').onclick=reset;
 window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp',' ','a','d','w','A','D','W'].includes(e.key)){e.preventDefault();if(['ArrowUp',' ','w','W'].includes(e.key)){if(!e.repeat)press('jump');}else press(['ArrowLeft','a','A'].includes(e.key)?'left':'right');}});
 window.addEventListener('keyup',e=>{if(['ArrowLeft','a','A'].includes(e.key))keys.delete('left');if(['ArrowRight','d','D'].includes(e.key))keys.delete('right');});window.addEventListener('blur',()=>keys.clear());
 function step(dt){
 if(won||dead)return;
 player.vx=((keys.has('right')?1:0)-(keys.has('left')?1:0))*scene.speed;
 if(jumpQueued&&player.ground){player.vy=-scene.jump;player.ground=false;}jumpQueued=false;
 player.x+=player.vx*dt;
 for(const s of solids)if(hit(player,s))player.x=player.vx>0?s.x-player.w:s.x+s.w;
 player.x=Math.max(0,Math.min(800-player.w,player.x));player.vy+=scene.gravity*dt;player.y+=player.vy*dt;player.ground=false;
 for(const s of solids)if(hit(player,s)){if(player.vy>=0){player.y=s.y-player.h;player.vy=0;player.ground=true;}else{player.y=s.y+s.h;player.vy=0;}}
 for(const c of coins)if(!c.taken&&hit(player,c))c.taken=true;
 for(const e of enemies){moveActor(e,e.movement||'chase',e.move_speed??scene.speed*.27,dt,player);if(hit(player,e))dead=true;}
 for(const [i,p] of pets.entries())moveActor(p,p.movement||'follow',p.move_speed??120,dt,{x:Math.max(0,player.x-40-(i%5)*25),y:Math.max(0,player.y-12-Math.floor(i/5)*16)});
 for(const d of decorations)moveActor(d,d.movement||'still',d.move_speed??120,dt,player);
 if(player.y>480)dead=true;
 if(hit(player,goal)&&coins.every(c=>c.taken))won=true;
 status.textContent=won?'You win! Your adventure is complete.':dead?'Try again! Press Restart.':`Coins: ${coins.filter(c=>c.taken).length} / ${coins.length} · Reach the flag`;
 }
 function render(){
 drawSceneBackground(ctx,scene.background);
 const object=(o)=>{if(scene.sprites?.[o.sprite]){drawSpritePixels(ctx,o,scene.sprites[o.sprite],performance.now());return;}ctx.fillStyle={platform:'#405678',coin:'#ffd36d',goal:'#b4a0ff',enemy:'#ff829d',pet:'#ddba86',decoration:'#ac9cdb',player:dead?'#71829d':'#5eead4'}[o.type];if(o.type==='coin'){ctx.beginPath();ctx.ellipse(o.x+o.w/2,o.y+o.h/2,o.w/2,o.h/2,0,0,Math.PI*2);ctx.fill();}else if(o.type==='goal'){ctx.fillRect(o.x,o.y,4,o.h);ctx.fillRect(o.x,o.y,o.w,o.h*.5);}else ctx.fillRect(o.x,o.y,o.w,o.h);if(o.type==='platform'){ctx.fillStyle='#5eead4';ctx.fillRect(o.x,o.y,o.w,5);}if(o.type==='player'||o.type==='enemy'){ctx.fillStyle='#15263d';ctx.fillRect(o.x+5,o.y+7,4,5);ctx.fillRect(o.x+o.w-9,o.y+7,4,5);}};
 for(const o of [...decorations,...solids,...coins.filter(c=>!c.taken),goal,...enemies,...pets,player])object(o);
 if(won||dead){ctx.fillStyle='#081020b8';ctx.fillRect(0,0,800,450);ctx.fillStyle='white';ctx.font='bold 38px system-ui';ctx.textAlign='center';ctx.fillText(won?'Adventure complete!':'Try again!',400,220);ctx.textAlign='start';}}

 function frame(t){const dt=Math.min((t-last)/1000||0,.025);last=t;step(dt);render();requestAnimationFrame(frame);}reset();requestAnimationFrame(frame);
})();

// Behaviour belongs to the object, never to its costume.
function moveActor(actor,movement,speed,dt,target){
 const distance=Math.max(0,speed)*dt;
 if(movement==='chase')actor.x+=Math.sign(target.x-actor.x)*Math.min(Math.abs(target.x-actor.x),distance);
 if(movement==='follow'){const dx=target.x-actor.x,dy=target.y-actor.y,length=Math.hypot(dx,dy);if(length>1){const step=Math.min(length,distance);actor.x+=dx/length*step;actor.y+=dy/length*step;}}
 if(movement==='patrol'){const min=Math.max(0,(actor.originX??actor.x)-80),max=Math.min(800-actor.w,(actor.originX??actor.x)+80);actor.x+=(actor.direction||1)*distance;if(actor.x>=max){actor.x=max;actor.direction=-1;}if(actor.x<=min){actor.x=min;actor.direction=1;}}
 actor.x=Math.max(0,Math.min(800-actor.w,actor.x));actor.y=Math.max(0,Math.min(450-actor.h,actor.y));
}
