/* Original neutral demo player. MIT. Ricardo Pupo Larguesa, Hermes Agent. */
(()=>{'use strict';
const root=new URL('../assets/',document.currentScript.src);
const canvas=document.getElementById('canvas'),c=canvas.getContext('2d');
const clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
window.D={c,canvas,clamp,smooth,mix:(a,b,p)=>a+(b-a)*p,
 rect(x,y,w,h,r,color){c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();},
 text(s,x,y,size=30,color='#172c29',weight=400,align='left'){c.fillStyle=color;c.font=`${weight} ${size}px Demo, sans-serif`;c.textAlign=align;c.fillText(s,x,y);},
 line(points,color,width=2){c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.stroke();},
 disk(x,y,r,color){c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fillStyle=color;c.fill();}
};
window.renderFrame=t=>{c.resetTransform();c.globalAlpha=1;c.globalCompositeOperation='source-over';c.setLineDash([]);c.shadowBlur=0;c.clearRect(0,0,canvas.width,canvas.height);c.save();window.scene(Math.max(0,Math.min(window.DURATION,Number(t)||0)));c.restore();};
window.draw=({t})=>{window.renderFrame(t);return canvas.toDataURL('image/jpeg',.94).split(',')[1];};
window.startDemo=()=>{
 window.ready=Promise.all([new FontFace('Demo',`url(${new URL('Rubik-400.ttf',root)})`,{weight:'400'}),new FontFace('Demo',`url(${new URL('Montserrat-800.ttf',root)})`,{weight:'800'})].map(f=>f.load().then(v=>document.fonts.add(v)))).then(()=>{
  document.getElementById('transcript').textContent=window.TRANSCRIPT;
  const play=document.getElementById('play'),replay=document.getElementById('replay'),seek=document.getElementById('seek'),status=document.getElementById('status');
  const exporting=new URLSearchParams(location.search).has('render'),media=matchMedia('(prefers-reduced-motion: reduce)');
  let paused=true,t=0,last=null;seek.max=window.DURATION;
  const label=()=>{play.textContent=paused?'Play':'Pause';play.setAttribute('aria-pressed',String(!paused));status.textContent=`${t.toFixed(1)} / ${window.DURATION.toFixed(1)} seconds`;seek.value=t;};
  play.onclick=()=>{if(t>=window.DURATION)t=0;paused=!paused;last=null;label();};
  replay.onclick=()=>{t=0;last=null;paused=media.matches;window.renderFrame(t);label();};
  seek.oninput=()=>{t=Number(seek.value);paused=true;last=null;window.renderFrame(t);label();};
  media.addEventListener('change',e=>{if(e.matches){paused=true;last=null;label();}});
  if(exporting)document.querySelector('nav').hidden=true;
  window.renderFrame(0);label();
  function tick(now){if(!paused){if(last!==null)t=Math.min(window.DURATION,t+(now-last)/1000);window.renderFrame(t);if(t>=window.DURATION)paused=true;label();}last=now;requestAnimationFrame(tick);}if(!exporting)requestAnimationFrame(tick);
 });return window.ready;
};
})();
