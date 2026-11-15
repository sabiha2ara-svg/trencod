'use strict';
const TrencodMusic=(()=>{
 const clean=m=>{if(m==null)return null;if(!m||typeof m.id!=='string'||! /^[a-f0-9]{24}$/.test(m.id)||typeof m.volume!=='number'||!Number.isFinite(m.volume)||m.volume<0||m.volume>1||typeof m.loop!=='boolean')throw Error('Invalid music settings. Choose the clip again.');return {id:m.id,volume:m.volume,loop:m.loop};};
 const url=m=>location.origin+'/media/music/'+clean(m).id;
 function markup(value){const m=clean(value);if(!m)return '';return `<section aria-label="Game music"><p>Music · Press play to listen</p><audio controls preload="none" ${m.loop?'loop':''} src="${url(m)}" onloadedmetadata="this.volume=${m.volume}" style="max-width:100%"></audio></section>`;}
 const pattern=/<!--trencod-music:([^>]+)-->([\s\S]*?)<!--\/trencod-music-->/g;
 function read(html){const match=[...html.matchAll(pattern)][0];try{return match?clean(JSON.parse(decodeURIComponent(match[1]))):null;}catch{return null;}}
 function insert(html,m){m=clean(m);html=html.replace(pattern,'');if(!m)return html;const block='<!--trencod-music:'+encodeURIComponent(JSON.stringify(m))+'-->\n'+markup(m)+'\n<!--/trencod-music-->';return /<\/body>/i.test(html)?html.replace(/<\/body>/i,block+'\n</body>'):html+'\n'+block;}
 return {clean,url,markup,read,insert};
})();
if(typeof module!=='undefined')module.exports=TrencodMusic;
if(typeof window!=='undefined')window.closeMusicPicker=()=>{const d=document.querySelector('#music-dialog');if(d){d.querySelector('audio')?.pause();d.remove();}};
async function musicPicker(value,apply){
 if(!user){toast('Sign in first to upload and save music.');showAuth();return;}
 window.closeMusicPicker();const version=routeVersion;
 const d=document.createElement('dialog');d.id='music-dialog';d.className='music-dialog';
 d.innerHTML='<div class="section-head"><h2>Music</h2><button data-close aria-label="Close music">Close</button></div><p>Choose a short loop for your animation or game.</p><label>Saved music<select data-library><option value="">Choose a clip…</option></select></label><label class="button">Upload music<input data-upload type="file" accept=".mp3,.ogg,.wav,audio/mpeg,audio/ogg,audio/wav"></label><p class="small">MP3, Ogg or WAV · Up to 300 KB each · 20 clips per account. Use music you own or have permission to share. Uploaded clips are accessible to anyone with their link. Exports need an internet connection to play music.</p><label>Volume <output data-volume-label>50%</output><input data-volume type="range" min="0" max="100" value="50"></label><label class="check"><input data-loop type="checkbox" checked> Loop music</label><audio data-preview controls preload="none" aria-label="Preview selected music"></audio><p data-status role="status">Loading saved music…</p><div class="actions"><button data-apply class="primary" disabled>Use this music</button><button data-remove>Remove music</button></div><p class="small">After applying, press Save in your editor. Removing music from a project keeps the clip in your library.</p>';
 document.body.append(d);d.showModal();const q=s=>d.querySelector(s),audio=q('audio'),select=q('[data-library]');
 const initial=TrencodMusic.clean(value);let selected=initial,uploading=false;
 function settings(){return select.value?{id:select.value,volume:Number(q('[data-volume]').value)/100,loop:q('[data-loop]').checked}:null;}
 function refresh(){selected=settings();q('[data-volume-label]').textContent=q('[data-volume]').value+'%';audio.volume=Number(q('[data-volume]').value)/100;audio.loop=q('[data-loop]').checked;q('[data-apply]').disabled=!selected||uploading;if(selected&&audio.getAttribute('src')!==TrencodMusic.url(selected)){audio.pause();audio.src=TrencodMusic.url(selected);}else if(!selected){audio.pause();audio.removeAttribute('src');}}
 function option(c){const o=document.createElement('option');o.value=c.id;o.textContent=c.name;select.append(o);}
 if(initial){q('[data-volume]').value=String(Math.round(initial.volume*100));q('[data-loop]').checked=initial.loop;}
 q('[data-close]').onclick=()=>d.close();d.onclose=window.closeMusicPicker;
 select.onchange=refresh;q('[data-volume]').oninput=refresh;q('[data-loop]').onchange=refresh;
 audio.onerror=()=>q('[data-status]').textContent='This clip could not play. Check the file format and your connection.';
 q('[data-apply]').onclick=()=>{if(version!==routeVersion)return window.closeMusicPicker();apply(settings());d.close();};
 q('[data-remove]').onclick=()=>{if(version===routeVersion)apply(null);d.close();};
 try{const r=await api('music');if(!d.isConnected||version!==routeVersion)return;for(const c of r.clips)option(c);if(initial&&!r.clips.some(c=>c.id===initial.id))option({id:initial.id,name:'Current project music (shared clip)'});if(initial)select.value=initial.id;q('[data-status]').textContent=r.clips.length+' / 20 clips saved';refresh();}catch(e){q('[data-status]').textContent=e.message;}
 q('[data-upload]').onchange=async e=>{const file=e.target.files[0];if(!file)return;if(file.size>300000){q('[data-status]').textContent='Choose a short clip up to 300 KB (compressed MP3 is usually smaller).';e.target.value='';return;}uploading=true;q('[data-upload]').disabled=true;refresh();q('[data-status]').textContent='Uploading…';try{const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=()=>reject(Error('Could not read this file.'));reader.readAsDataURL(file);});const r=await api('music',{name:file.name.slice(0,80),data});if(!d.isConnected||version!==routeVersion)return;option(r.clip);select.value=r.clip.id;q('[data-status]').textContent='Uploaded. Press Use this music, then Save your project.';}catch(e){q('[data-status]').textContent=e.message;}finally{uploading=false;q('[data-upload]').disabled=false;refresh();e.target.value='';}};
}
