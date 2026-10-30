/* A short opening splash, not a replayable feature. No visible controls. */
(() => {
  'use strict';
  if(location.protocol==='file:'&&!document.documentElement.hasAttribute('data-intro-preview'))return;
  const iconURL=new URL('trencod-icon.png',document.currentScript.src).href;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const duration=reduced?700:2500;
  function start(){
    try{if(sessionStorage.getItem('trencod-intro-seen-v04'))return;sessionStorage.setItem('trencod-intro-seen-v04','1');}catch(_){}
    const previous=document.activeElement,dialog=document.createElement('dialog');
    let audio=null,closed=false,timer,voices=[];
    const started=performance.now();
    dialog.className='trencod-intro';dialog.setAttribute('aria-label','Welcome to Trencod');
    dialog.innerHTML=`<div class="intro-stage"><div class="intro-grid"></div><div class="intro-glow"></div><div class="intro-symbol"><span class="intro-ring"></span><span class="intro-ring second"></span><img class="intro-icon" src="${iconURL}" alt="Trencod spark mascot" width="182" height="182"></div><h1 class="intro-word" aria-label="trencod">${[...'trencod'].map((letter,i)=>`<span aria-hidden="true" class="intro-letter" style="--i:${i}">${letter}</span>`).join('')}</h1><p class="intro-tagline">PLAY. CREATE. REMIX.</p><div aria-hidden="true"><i class="intro-dot"></i><i class="intro-dot"></i><i class="intro-dot"></i><i class="intro-dot"></i></div></div>`;
    function close(){if(closed)return;closed=true;clearTimeout(timer);for(const v of voices){try{v.stop();}catch(_){}}if(audio)audio.close().catch(()=>{});dialog.close();dialog.remove();if(previous?.isConnected)previous.focus({preventScroll:true});}
    async function unlock(){
      if(closed||audio||reduced)return;
      const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)return;
      try{
        audio=new Audio();await audio.resume();if(closed||audio.state!=='running')return;
        const elapsed=(performance.now()-started)/1000;
        for(const [offset,high,low,length,volume] of [[.25,580,160,.23,.10],[.68,760,220,.2,.08],[1.2,1000,420,.12,.06],[1.48,660,660,.18,.04]]){
          if(offset<elapsed)continue;
          const at=audio.currentTime+offset-elapsed,osc=audio.createOscillator(),gain=audio.createGain();osc.frequency.setValueAtTime(high,at);osc.frequency.exponentialRampToValueAtTime(low,at+length*.8);gain.gain.setValueAtTime(0,at);gain.gain.linearRampToValueAtTime(volume,at+.012);gain.gain.exponentialRampToValueAtTime(.001,at+length);osc.connect(gain);gain.connect(audio.destination);osc.start(at);osc.stop(at+length+.03);voices.push(osc);osc.onended=()=>{osc.disconnect();gain.disconnect();};
        }
      }catch(_){} // Autoplay restrictions never delay or restart the splash.
    }
    dialog.addEventListener('cancel',e=>{e.preventDefault();close();});
    dialog.addEventListener('pointerdown',unlock,{once:true});
    dialog.addEventListener('keydown',unlock,{once:true});
    document.body.appendChild(dialog);dialog.showModal();timer=setTimeout(close,duration);
    if(navigator.userActivation?.hasBeenActive)unlock();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
