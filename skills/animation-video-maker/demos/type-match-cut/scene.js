/* Original semantic match-cut: punctuation becomes a bridge. */
(()=>{'use strict';const {c,rect,text,line,disk,smooth,mix}=D;
window.DURATION=10;
window.TRANSCRIPT='Give ideas space. Then make a connection. The letters of SPACE move apart. Its underline becomes a bridge across the gap. Two points meet at the center, leaving the statement: Make a connection. Original typographic study.';
window.scene=t=>{
 const spread=smooth((t-.7)/1.5),cut=smooth((t-3.7)/1.2),join=smooth((t-5.4)/1.5),finish=smooth((t-7.5)/.9);
 rect(0,0,1280,720,0,'#f74c37');text('WORDS IN MOTION',62,65,18,'#241b1c',800);text('02 / SPACE TO CONNECTION',1218,65,16,'#241b1c',400,'right');
 c.save();c.globalAlpha=1-smooth(cut*2);text('Give ideas',64,229,58,'#241b1c',800);const gap=mix(136,225,spread);'SPACE'.split('').forEach((s,i)=>text(s,640+(i-2)*gap,428,142,'#fff5db',800,'center'));text('A little distance changes what you see.',66,616,22,'#241b1c');c.restore();
 // Preserve the underline's y coordinate and cream color through the match-cut.
 const yy=mix(472,367,cut),left=mix(132,178,cut),right=mix(1148,1102,cut),hole=190*cut*(1-join);
 line([[left,yy],[640-hole,yy]],'#fff5db',mix(12,18,cut));line([[640+hole,yy],[right,yy]],'#fff5db',mix(12,18,cut));
 c.save();c.globalAlpha=smooth((cut-.5)*2)*(1-smooth((t-7.1)/.4));text('Then make',64,211,57,'#241b1c',800);text('a connection.',64,276,57,'#241b1c',800);
 disk(mix(258,620,join),yy-42,24,'#241b1c');disk(mix(1022,660,join),yy-42,24,'#fff5db');
 line([[left,yy+19],[left,yy+120]],'#241b1c',4);line([[right,yy+19],[right,yy+120]],'#241b1c',4);text('ONE IDEA',left,yy+163,18,'#241b1c',800);text('ANOTHER POSSIBILITY',right,yy+163,18,'#241b1c',800,'right');c.restore();
 c.save();if(finish>0)rect(0,108,1280,490,0,'#241b1c');c.globalAlpha=finish;text('Make a',64,278,96,'#fff5db',800);text('connection.',64,404,112,'#fff5db',800);line([[70,462],[1210,462]],'#f74c37',12);disk(640,462,22,'#fff5db');text('Not more noise. A meaningful link.',68,538,27,'#fff5db');c.restore();
 text('A TYPOGRAPHIC STUDY',62,675,16,'#241b1c',800);text('DISTANCE  /  RELATIONSHIP',1218,675,16,'#241b1c',400,'right');
};})();
