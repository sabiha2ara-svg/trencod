'use strict';
function vectorShape(kind,x,y,w,h,fill,extra={}){return {kind,x,y,w,h,fill,stroke:'none',sw:0,rotation:0,...extra};}
function vectorMarkup(art){
 const attrs=s=>`fill="${s.fill}" stroke="${s.stroke}" stroke-width="${s.sw}" stroke-linecap="round" stroke-linejoin="round"`;
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">'+art.shapes.map(s=>{
  let body=s.kind==='ellipse'?`<ellipse cx="${s.w/2}" cy="${s.h/2}" rx="${s.w/2}" ry="${s.h/2}" ${attrs(s)}/>`:s.kind==='rect'?`<rect width="${s.w}" height="${s.h}" ${attrs(s)}/>`:`<path d="${s.points.map((p,i)=>(i?'L':'M')+p[0]*s.w/256+' '+p[1]*s.h/256).join(' ')}${s.closed?' Z':''}" ${attrs(s)}/>`;
  return `<g transform="translate(${s.x} ${s.y}) rotate(${s.rotation} ${s.w/2} ${s.h/2})">${body}</g>`;
 }).join('')+'</svg>';
}
function drawVectorSprite(ctx,o,art){ctx.save();ctx.translate(o.x,o.y);ctx.scale(o.w/256,o.h/256);for(const s of art.shapes){ctx.save();ctx.translate(s.x+s.w/2,s.y+s.h/2);ctx.rotate(s.rotation*Math.PI/180);ctx.translate(-s.w/2,-s.h/2);ctx.beginPath();if(s.kind==='ellipse')ctx.ellipse(s.w/2,s.h/2,s.w/2,s.h/2,0,0,Math.PI*2);else if(s.kind==='rect')ctx.rect(0,0,s.w,s.h);else {s.points.forEach((p,i)=>ctx[i?'lineTo':'moveTo'](p[0]*s.w/256,p[1]*s.h/256));if(s.closed)ctx.closePath();}if(s.fill!=='none'){ctx.fillStyle=s.fill;ctx.fill();}if(s.stroke!=='none'&&s.sw){ctx.strokeStyle=s.stroke;ctx.lineWidth=s.sw;ctx.lineJoin=ctx.lineCap='round';ctx.stroke();}ctx.restore();}ctx.restore();}
function vectorLibrary(){
 const R=(x,y,w,h,c)=>vectorShape('rect',x,y,w,h,c),E=(x,y,w,h,c)=>vectorShape('ellipse',x,y,w,h,c),P=(points,c)=>vectorShape('path',0,0,256,256,c,{points,closed:true});
 const ink='#243047',white='#fff6df',lib=[];const add=(name,category,shapes)=>lib.push({type:'vector',name,category,shapes});
 const animals=['Dog','Cat','Fox','Bear','Rabbit','Panda','Tiger','Lion','Wolf','Mouse','Pig','Frog','Owl','Penguin','Chicken','Duck','Monkey','Koala','Raccoon','Deer'];
 const coats=['#c98a55','#bc9bed','#ed8a38','#996b48','#efcece','#eeeeee','#efad46','#d79d37','#94a6b9','#a9a4b5','#f4a4b9','#65c47d','#b98a60','#303e54','#f5e6bd','#f2d363','#af784d','#aab3b9','#8d9ba6','#c6a17a'];
 animals.forEach((name,i)=>{const c=coats[i],s=[];if(['Cat','Fox','Wolf','Tiger','Raccoon'].includes(name)){s.push(P([[40,110],[34,25],[104,72]],c),P([[152,72],[222,25],[216,110]],c));}else if(name==='Rabbit'){s.push(E(65,4,43,120,c),E(148,4,43,120,c),E(77,15,18,80,'#ed97af'),E(160,15,18,80,'#ed97af'));}else {s.push(E(26,42,70,78,c),E(160,42,70,78,c));}if(name==='Lion')s.push(E(25,38,206,204,'#a76534'));s.push(E(43,65,170,166,c),E(70,150,116,66,white));if(['Panda','Raccoon'].includes(name))s.push(E(63,102,55,55,ink),E(138,102,55,55,ink));if(name==='Frog')s.push(E(45,55,68,68,c),E(143,55,68,68,c));if(name==='Owl')s.push(E(57,91,68,82,white),E(131,91,68,82,white));s.push(E(83,116,16,23,ink),E(157,116,16,23,ink));if(['Duck','Chicken','Penguin','Owl'].includes(name))s.push(P([[103,158],[153,158],[128,185]],'#eea54b'));else s.push(E(115,159,26,19,ink));if(name==='Pig')s.push(E(99,148,58,39,'#dc7e97'),E(110,159,9,12,ink),E(137,159,9,12,ink));if(name==='Tiger')s.push(P([[115,65],[125,105],[135,65]],ink),P([[44,138],[77,147],[44,157]],ink),P([[212,138],[179,147],[212,157]],ink));if(name==='Deer')s.push(P([[70,69],[49,15],[62,17],[83,63]],'#886342'),P([[186,69],[207,15],[194,17],[173,63]],'#886342'));if(name==='Chicken')s.push(E(108,40,40,40,'#ed657b'));
 if(['Dog','Bear','Mouse','Monkey','Koala'].includes(name)){s.push(E(40,58,31,41,name==='Koala'?'#dddddf':'#d6aaa0'),E(185,58,31,41,name==='Koala'?'#dddddf':'#d6aaa0'));}
 if(name==='Monkey')s.push(E(74,87,46,64,'#e4b785'),E(136,87,46,64,'#e4b785'),E(89,113,14,22,ink),E(153,113,14,22,ink));
 if(['Cat','Mouse'].includes(name))s.push(vectorShape('path',0,0,256,256,'none',{points:[[45,156],[92,166],[44,179]],stroke:ink,sw:3,closed:false}),vectorShape('path',0,0,256,256,'none',{points:[[211,156],[164,166],[212,179]],stroke:ink,sw:3,closed:false}));
 if(name==='Dog')s.push(E(65,89,29,23,'#9a623f'));
 if(name==='Penguin')s.push(E(70,95,42,56,white),E(144,95,42,56,white),E(84,113,14,22,ink),E(158,113,14,22,ink));
 const face=s.map(o=>({...o,x:o.x*.72+36,y:o.y*.72,w:o.w*.72,h:o.h*.72,sw:o.sw*.72}));
 const body=[E(73,143,110,95,c),E(94,157,68,73,white),E(49,157,42,61,c),E(165,157,42,61,c),E(66,214,57,30,c),E(133,214,57,30,c)];
 add(name,'Animals',[...body,...face]);});
 add('Robot','Characters',[R(53,62,150,146,'#72cfd0'),R(116,30,24,34,ink),E(111,15,34,30,'#ffcf65'),R(70,99,42,34,ink),R(145,99,42,34,ink),R(87,164,84,16,white)]);
 add('Ghost','Characters',[E(48,35,160,180,'#e7dcfa'),P([[48,126],[208,126],[208,229],[176,205],[144,229],[112,205],[80,229],[48,205]],'#e7dcfa'),E(86,101,22,34,ink),E(148,101,22,34,ink)]);
 add('Slime','Characters',[E(33,74,190,151,'#7cdb9a'),E(78,123,20,26,ink),E(157,123,20,26,ink),E(113,167,30,15,'#32795d')]);
 add('Alien','Characters',[E(48,35,160,178,'#9fd77e'),E(72,92,40,64,ink),E(144,92,40,64,ink),R(108,183,40,8,ink)]);
 add('Astronaut','Characters',[R(66,132,124,98,'#eeeaf9'),E(40,22,176,163,'#eeeaf9'),E(60,42,136,117,'#547ba7'),E(80,53,44,32,'#a8daf2'),R(104,185,48,25,'#f2b057')]);
 add('Tree','Nature',[R(108,128,40,110,'#9e714b'),E(30,30,135,135,'#55b981'),E(104,45,125,126,'#79cf83')]);
 add('Pine','Nature',[R(110,180,36,60,'#9e714b'),P([[128,15],[35,144],[80,144],[23,209],[233,209],[176,144],[221,144]],'#4aab7e')]);
 add('Flower','Nature',[R(118,110,20,130,'#63ac79'),E(135,160,65,30,'#63ac79'),E(38,73,90,70,'#ed8eb1'),E(128,73,90,70,'#ed8eb1'),E(84,22,90,85,'#ed8eb1'),E(84,112,90,85,'#ed8eb1'),E(92,75,72,72,'#ffdb77')]);
 add('Mushroom','Nature',[R(98,116,60,112,'#f3dcb9'),E(29,43,198,132,'#ed7b72'),E(67,65,37,33,white),E(147,97,37,33,white)]);
 add('Cloud','Nature',[E(30,105,196,80,'#e1eafb'),E(55,65,100,105,'#e1eafb'),E(115,78,91,88,'#e1eafb')]);
 add('Sun','Nature',[...Array.from({length:8},(_,i)=>vectorShape('rect',119,10,18,236,'#efb453',{rotation:i*45})),E(53,53,150,150,'#ffdf7a')]);
 add('Moon','Nature',[E(42,24,170,205,'#d3c4fa'),E(81,65,36,36,'#b9a3e8'),E(135,144,40,44,'#b9a3e8')]);
 add('Mountain','Nature',[P([[15,229],[112,27],[241,229]],'#7c9eb5'),P([[112,27],[72,109],[113,91],[151,107]],'#e8f0fa')]);
 add('Rock','Nature',[P([[29,198],[49,97],[115,61],[201,92],[234,198],[160,227],[80,225]],'#93a3ad'),P([[49,97],[115,61],[103,166],[29,198]],'#b8c5cb')]);
 add('Bush','Nature',[E(22,117,94,105,'#70c184'),E(79,73,107,146,'#63b67d'),E(145,116,91,106,'#80d58d')]);
 add('Star','Objects',[P(Array.from({length:10},(_,i)=>{const a=i*Math.PI/5-Math.PI/2,r=i%2?48:111;return [128+Math.cos(a)*r,128+Math.sin(a)*r];}),'#ffcf68')]);
 add('Heart','Objects',[E(35,43,100,103,'#f28da7'),E(121,43,100,103,'#f28da7'),P([[37,111],[219,111],[128,226]],'#f28da7')]);
 add('Coin','Objects',[E(35,27,186,202,'#e9a344'),E(53,45,150,166,'#ffdb72'),R(117,75,22,105,'#d9963e')]);
 add('Gem','Objects',[P([[62,40],[194,40],[237,99],[128,231],[19,99]],'#65cdda'),P([[62,40],[128,40],[90,99],[19,99]],'#b0eced'),P([[90,99],[237,99],[128,231]],'#389ba9')]);
 add('Key','Objects',[E(27,37,109,109,'#ffce6c'),E(55,65,53,53,ink),P([[107,112],[136,89],[229,183],[211,202],[187,180],[170,198],[150,178],[166,160]],'#ffce6c')]);
 add('Flag','Objects',[R(49,19,15,218,'#d9dfeb'),P([[64,25],[222,25],[181,86],[222,140],[64,140]],'#ae9bef')]);
 add('Chest','Objects',[R(34,75,188,149,'#a8754d'),R(34,75,188,53,'#d49b5c'),R(55,75,18,149,'#f5cb69'),R(183,75,18,149,'#f5cb69'),R(109,111,38,45,'#f5cb69')]);
 add('House','Objects',[R(49,111,158,122,'#edc59a'),P([[17,119],[128,24],[239,119]],'#de7c72'),R(109,155,40,78,'#885b4d'),R(64,145,30,35,'#8ecddc')]);
 add('Castle','Objects',[R(35,80,186,153,'#b5afc9'),R(19,32,55,201,'#c5bed9'),R(182,32,55,201,'#c5bed9'),E(100,158,56,84,'#6f6688'),R(101,196,54,37,'#6f6688'),R(35,58,18,27,'#6f6688'),R(201,58,18,27,'#6f6688')]);
 add('Rocket','Objects',[P([[99,142],[37,219],[95,200]],'#ed8a78'),P([[157,142],[219,219],[161,200]],'#ed8a78'),E(83,22,90,192,'#dddff3'),E(101,80,54,54,'#6cbbd3'),P([[102,205],[154,205],[128,250]],'#f9c16c')]);
 add('Car','Objects',[R(30,120,196,71,'#8cabe7'),P([[68,121],[87,64],[168,64],[198,121]],'#8cabe7'),R(95,77,67,39,'#daf0f5'),E(54,167,45,45,ink),E(163,167,45,45,ink)]);
 add('Boat','Objects',[P([[20,163],[236,163],[199,224],[62,224]],'#ac7d55'),R(120,23,10,142,ink),P([[111,40],[37,145],[111,145]],'#f3e4c1'),P([[139,45],[217,145],[139,145]],'#a4c7df')]);
 add('Burger','Food',[E(35,35,186,116,'#eac071'),R(34,104,188,28,'#75bb6f'),R(32,135,192,33,'#84523f'),R(34,172,188,22,'#f5cb66'),E(35,176,186,53,'#eac071')]);
 add('Apple','Food',[R(121,25,12,44,'#936747'),E(133,24,61,28,'#74b681'),E(38,67,112,157,'#e87c7d'),E(105,67,112,157,'#e87c7d')]);
 add('Potion','Objects',[R(97,23,62,51,'#a77f59'),R(102,64,52,70,'#b7e1ed'),E(52,98,152,137,'#b7e1ed'),E(68,134,120,85,'#b49aee')]);
 return lib;
}
