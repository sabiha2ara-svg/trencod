/* Apply theme before styles load, so saved light mode does not flash dark. */
(() => {
  const key='trencod-theme',root=document.documentElement;
  const system=window.matchMedia('(prefers-color-scheme: dark)');
  let chosen=null;
  try { const saved=localStorage.getItem(key);if(saved==='dark'||saved==='light')chosen=saved; } catch (_) {}
  function apply(theme){
    root.dataset.theme=theme;
    root.style.colorScheme=theme;
    const button=document.getElementById('theme-toggle');
    if(button){button.textContent=theme==='dark'?'☀ Light':'☾ Dark';button.setAttribute('aria-label','Switch to '+(theme==='dark'?'light':'dark')+' mode');button.setAttribute('aria-pressed',String(theme==='light'));}
  }
  apply(chosen||(system.matches?'dark':'light'));
  function bind(){const b=document.getElementById('theme-toggle');if(!b)return;apply(root.dataset.theme);b.addEventListener('click',()=>{chosen=root.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem(key,chosen);}catch(_){}apply(chosen);});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
  system.addEventListener('change',()=>{if(!chosen)apply(system.matches?'dark':'light');});
  window.addEventListener('storage',e=>{if(e.key!==key)return;chosen=['dark','light'].includes(e.newValue)?e.newValue:null;apply(chosen||(system.matches?'dark':'light'));});
})();
