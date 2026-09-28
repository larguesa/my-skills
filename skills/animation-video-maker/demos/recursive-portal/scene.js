/* Original portrait recursion. Fixed layer count, absolute-time transforms. */
(()=>{'use strict';const {c,rect,text,line,disk}=D;
window.DURATION=8;
window.TRANSCRIPT='Within, another world. Nested rounded portals rotate gently inside a tall midnight field. Lavender, apricot and green contours recede toward a luminous central seed. The geometry returns to its opening configuration. Abstract procedural artwork, not scientific data.';
window.scene=t=>{
 const phase=2*Math.PI*t/8;
 rect(0,0,720,1280,0,'#101c28');
 for(let i=0;i<70;i++){const x=38+(i*137)%644,y=210+(i*199)%850;disk(x,y,i%3===0?1.5:.7,'#6f858f');}
 text('SPATIAL STUDY / 03',48,68,18,'#b9c8cb',400);text('Within,',46,146,63,'#f2e8d6',800);text('another world.',48,191,30,'#b9c8cb');
 c.save();c.beginPath();c.roundRect(30,239,660,816,320);c.clip();
 for(let i=0;i<19;i++){
  const pulse=1+.048*Math.sin(phase-i*.34),scale=Math.pow(.855,i)*pulse,w=750*scale,h=980*scale;
  c.save();c.translate(360+14*Math.sin(phase+i*.3)*scale,650+12*Math.cos(phase+i*.25)*scale);c.rotate(.105*Math.sin(phase-i*.29));
  const colors=['#cab9e7','#f2bc91','#285e60','#152f3d'];rect(-w/2,-h/2,w,h,Math.min(w/2,180*scale),colors[i%4]);
  c.strokeStyle='#fff6e33a';c.lineWidth=1.4;c.stroke();c.restore();
 }
 c.restore();
 const glow=c.createRadialGradient(360,650,0,360,650,58);glow.addColorStop(0,'#fff4caaa');glow.addColorStop(1,'#fff4ca00');disk(360,650,58,glow);disk(360,650,7,'#fff4ca');
 line([[48,1120],[672,1120]],'#50616d',1);text('A FRAME INSIDE A FRAME',48,1162,18,'#f2e8d6',800);text('A quiet journey with no final edge.',48,1204,21,'#b9c8cb');
};})();
