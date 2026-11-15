'use strict';
async function inboxBadge(){const link=$('#inbox-link');if(!link)return;if(!user){link.textContent='Inbox';return;}try{const id=user.id,r=await api('inbox');if(user?.id===id)link.textContent=r.unread?'Inbox · '+r.unread:'Inbox';}catch{}}
async function inboxPage(version){
 if(!user){signInPanel('Your notifications');return;}
 const r=await api('inbox');if(version!==routeVersion)return;
 app.innerHTML=`<div class="toolbar"><div><span class="eyebrow">YOUR CREATOR COMMUNITY</span><h1>Inbox</h1></div><div class="actions"><button id="refresh-inbox">Refresh</button><button id="read-inbox">Mark all read</button></div></div><p>Follows, game comments, public remixes, playtest feedback and sales. Latest 100 events; refresh to check for updates.</p><div>${r.events.map(e=>`<article class="notice"><a class="button" href="#${esc(e.link)}">${e.unread?'● ':''}${esc(e.message)}</a><p class="small">${esc(new Date(e.created*1000).toLocaleString())}</p></article>`).join('')||'<div class="empty">All quiet for now. Publish a game or meet other creators.</div>'}</div>`;
 $('#refresh-inbox').onclick=()=>route();$('#read-inbox').onclick=async()=>{try{await api('inbox/read',{until:r.until});await route();}catch(e){toast(e.message);}};
}
async function queueButton(pid,version){
 const holder=document.createElement('div');holder.className='actions';holder.innerHTML='<button id="queue-game">Save for later</button><a class="button" href="#later">Play later list</a>';app.appendChild(holder);
 let saved=false;
 const render=()=>{const b=holder.querySelector('button');b.textContent=saved?'Remove from Play later':'Save for later';b.setAttribute('aria-pressed',String(saved));};
 if(user){try{const r=await api('play-later');if(version!==routeVersion)return;saved=r.projects.some(p=>p.id===pid);render();}catch(e){toast(e.message);}}
 holder.querySelector('button').onclick=()=>{const action=async()=>{try{const r=await api('play-later');saved=r.projects.some(p=>p.id===pid);await api('play-later',{id:pid,saved:!saved});saved=!saved;render();toast(saved?'Added to your private Play later list.':'Removed from your list.');}catch(e){toast(e.message);}};if(requireUser(action))action();};
}
async function historyPage(pid,version){
 if(!user){signInPanel('Your project history');return;}
 if(!pid){location.hash='mine';return;}
 const r=await api('history/'+encodeURIComponent(pid));if(version!==routeVersion)return;
 app.innerHTML=`<span class="eyebrow">SAVED CODE HISTORY</span><h1>${esc(r.title)}</h1><p>Last 20 previous saved versions. Preview or download before restoring. Restore keeps your current code in history and makes the project a private draft.</p><p class="small">History starts with edits made in version 0.8. Visual projects store generated code here; scene layouts are not restored. Use Code after restoring, or export your scene JSON from the Visual editor.</p><a class="button" href="#studio/${esc(pid)}">Back to Code</a><div>${r.versions.map(v=>`<article class="notice"><h3>${esc(v.title)}</h3><p>${esc(new Date(v.saved*1000).toLocaleString())}</p><div class="actions"><button data-history-preview="${v.id}">Preview</button><button data-history-download="${v.id}">Download code JSON</button><button data-history-restore="${v.id}">Restore as draft</button></div></article>`).join('')||'<div class="empty">No previous versions yet. Save a change to this project to start its history.</div>'}</div>`;
 document.querySelectorAll('[data-history-preview]').forEach(b=>b.onclick=()=>codePreview('history/'+encodeURIComponent(pid)+'/'+b.dataset.historyPreview));
 document.querySelectorAll('[data-history-download]').forEach(b=>b.onclick=async()=>{try{const v=await api('history/'+encodeURIComponent(pid)+'/'+b.dataset.historyDownload);download(JSON.stringify(v.code,null,2),'trencod-version-'+b.dataset.historyDownload+'.json','application/json');}catch(e){toast(e.message);}});
 document.querySelectorAll('[data-history-restore]').forEach(b=>b.onclick=async()=>{if(!confirm('Restore this saved code and make the game private? Your current code stays in history. Publish again when ready.'))return;try{b.disabled=true;await api('history/restore',{id:pid,version:Number(b.dataset.historyRestore),updated:r.updated});location.hash='studio/'+pid;toast('Restored as a private draft.');}catch(e){toast(e.message);b.disabled=false;}});
}
