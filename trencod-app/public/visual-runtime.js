(()=>{
 const canvas=document.querySelector('#game'),ctx=canvas.getContext('2d'),status=document.querySelector('#game-status'),keys=new Set();
 const solids=scene.objects.filter(o=>o.type==='platform'),spawn=scene.objects.find(o=>o.type==='player'),goal=scene.objects.find(o=>o.type==='goal');
 let player,coins,enemies,won=false,dead=false,jumpQueued=false,last=0;
 const hit=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
 function reset(){player={...spawn,vx:0,vy:0,ground:false};coins=scene.objects.filter(o=>o.type==='coin').map(o=>({...o,taken:false}));enemies=scene.objects.filter(o=>o.type==='enemy').map(o=>({...o}));won=dead=false;keys.clear();jumpQueued=false;status.textContent='Collect all coins, avoid enemies, then reach the flag.';}
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
 for(const e of enemies){e.x+=Math.sign(player.x-e.x)*scene.speed*.27*dt;e.x=Math.max(0,Math.min(800-e.w,e.x));if(hit(player,e))dead=true;}
 if(player.y>480)dead=true;
 if(hit(player,goal)&&coins.every(c=>c.taken))won=true;
 status.textContent=won?'You win! Your adventure is complete.':dead?'Try again! Press Restart.':`Coins: ${coins.filter(c=>c.taken).length} / ${coins.length} · Reach the flag`;
 }
 function render(){ctx.clearRect(0,0,800,450);ctx.fillStyle='#14233f';ctx.fillRect(0,0,800,450);ctx.fillStyle='#263a5c';for(let x=0;x<800;x+=80){ctx.beginPath();ctx.arc(x+30,90+(x%3)*20,35,0,Math.PI*2);ctx.fill();}for(const s of solids){ctx.fillStyle='#405678';ctx.fillRect(s.x,s.y,s.w,s.h);ctx.fillStyle='#5eead4';ctx.fillRect(s.x,s.y,s.w,5);}for(const c of coins)if(!c.taken){ctx.fillStyle='#ffd36d';ctx.beginPath();ctx.ellipse(c.x+c.w/2,c.y+c.h/2,c.w/2,c.h/2,0,0,Math.PI*2);ctx.fill();}ctx.fillStyle='#c2b0ff';ctx.fillRect(goal.x,goal.y,4,goal.h);ctx.fillStyle='#b4a0ff';ctx.fillRect(goal.x,goal.y,goal.w,goal.h*.5);for(const e of enemies){ctx.fillStyle='#ff829d';ctx.fillRect(e.x,e.y,e.w,e.h);ctx.fillStyle='#331b39';ctx.fillRect(e.x+5,e.y+6,5,5);ctx.fillRect(e.x+e.w-10,e.y+6,5,5);}ctx.fillStyle=dead?'#71829d':'#5eead4';ctx.fillRect(player.x,player.y,player.w,player.h);ctx.fillStyle='#15263d';ctx.fillRect(player.x+5,player.y+7,4,5);ctx.fillRect(player.x+player.w-9,player.y+7,4,5);if(won||dead){ctx.fillStyle='#081020b8';ctx.fillRect(0,0,800,450);ctx.fillStyle='white';ctx.font='bold 38px system-ui';ctx.textAlign='center';ctx.fillText(won?'Adventure complete!':'Try again!',400,220);}}
 function frame(t){const dt=Math.min((t-last)/1000||0,.025);last=t;step(dt);render();requestAnimationFrame(frame);}reset();requestAnimationFrame(frame);
})();
