/* Original shared preview runtime. No API, tracking, or remote resources. */
(() => {
'use strict';
const base=new URL('.',document.currentScript.src), canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d');
const ink='#22262b',blue='#3264ff',cyan='#00b4e8';
const darkLogo=new Image(),lightLogo=new Image();darkLogo.src=window.T2S_LOGOS.dark;lightLogo.src=window.T2S_LOGOS.light;
let info={};
const clamp=x=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
function text(s,x,y,size=40,color=ink,weight=400,align='left',family){ctx.fillStyle=color;ctx.font=`${weight} ${size}px ${family||(weight>=700?'BrandTitle':'BrandBody')}, sans-serif`;ctx.textAlign=align;ctx.fillText(s,x,y);ctx.textAlign='left';}
function line(points,color=blue,width=3,progress=1){if(points.length<2)return;let lengths=[],total=0;for(let i=1;i<points.length;i++){let l=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lengths.push(l);total+=l;}let remaining=total*clamp(progress);ctx.beginPath();ctx.moveTo(...points[0]);for(let i=1;i<points.length;i++){let l=lengths[i-1];if(remaining>=l){ctx.lineTo(...points[i]);remaining-=l;}else{let f=l?remaining/l:0;ctx.lineTo(points[i-1][0]+(points[i][0]-points[i-1][0])*f,points[i-1][1]+(points[i][1]-points[i-1][1])*f);break;}}ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.lineJoin='round';ctx.stroke();}
function frame(bg='#f5f8fc',dark=false,tag=''){ctx.fillStyle=bg;ctx.fillRect(0,0,1920,1080);let logo=dark?lightLogo:darkLogo;ctx.drawImage(logo,96,62,140,140*logo.height/logo.width);text(info.service,285,105,30,dark?'#f6f8fc':ink);text(tag,1824,105,23,dark?'#a1b5cb':'#647381',400,'right');text('T2S Tech · '+info.title,96,1002,25,dark?'#a1b5cb':'#647381');}
function end(){frame('#101c2d',true,'NEXT STEP');text('Evidence before expansion.',96,340,74,'#ffffff',800);text('Start a technical conversation.',100,450,44,'#c9dae8');ctx.fillStyle=blue;ctx.fillRect(96,575,1100,136);text('t2stech.com/contact',140,665,60,'#ffffff',800);line([[1370,350],[1650,350],[1650,650],[1420,650]],cyan,8);line([[1540,540],[1650,650],[1760,540]],cyan,8);text('Software that matters.',100,820,36,'#ffffff');}
window.A={ctx,canvas,ink,blue,cyan,clamp,ease,text,line,frame};
window.DURATION=20;
window.renderFrame=t=>{t=Math.max(0,Math.min(20,Number(t)||0));ctx.resetTransform();ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';ctx.setLineDash([]);ctx.shadowBlur=0;ctx.shadowOffsetX=0;ctx.shadowOffsetY=0;ctx.clearRect(0,0,1920,1080);ctx.save();if(t>=17)end();else window.scene(t);ctx.restore();};
window.draw=({t})=>{window.renderFrame(t);return canvas.toDataURL('image/jpeg',.94).split(',')[1];};
A.start=options=>{
 info=options;canvas.setAttribute('role','img');canvas.setAttribute('aria-label',options.description||options.title);
 const fonts=[new FontFace('BrandTitle',`url(${new URL('Montserrat-800.ttf',base)})`,{weight:'800'}),new FontFace('BrandBody',`url(${new URL('Rubik-400.ttf',base)})`,{weight:'400'})];
 window.ready=Promise.all([...fonts.map(f=>f.load().then(v=>document.fonts.add(v))),darkLogo.decode(),lightLogo.decode()]).then(()=>{
  let t=0,last=null,paused=new URLSearchParams(location.search).has('render')||matchMedia('(prefers-reduced-motion: reduce)').matches;
  const exporting=new URLSearchParams(location.search).has('render'),play=document.getElementById('play'),replay=document.getElementById('replay');
  const label=()=>{play.textContent=paused?'Play':'Pause';play.setAttribute('aria-pressed',String(!paused));};
  play.onclick=()=>{if(t>=20)t=0;paused=!paused;last=null;label();};replay.onclick=()=>{t=0;paused=false;last=null;label();};
  if(exporting){play.style.display='none';replay.style.display='none';document.body.classList.add('export');}
  label();window.renderFrame(0);
  function tick(now){if(!paused){if(last!==null)t=Math.min(20,t+(now-last)/1000);window.renderFrame(t);if(t>=20){paused=true;label();}}last=now;requestAnimationFrame(tick);}if(!exporting)requestAnimationFrame(tick);
 });return window.ready;
};
})();
