/* Original continuous UI object choreography, not product footage. */
(()=>{'use strict';const {c,rect,text,line,disk,smooth,mix}=D;
window.DURATION=9;
window.TRANSCRIPT='One thought. Many forms. An illustrative idea chip expands into a planning card, separates into three workflow columns, and gathers back into the original chip. Capture. Arrange. Focus. This is a fictional interface study, not footage of a real product.';
window.scene=t=>{
 const a=smooth((t-1)/1.2),b=smooth((t-3.7)/1.2),d=smooth((t-6.8)/1.4),open=a*(1-d),board=b*(1-d);
 rect(0,0,1280,720,0,'#f1f0e8');
 for(let x=40;x<1280;x+=40)for(let y=40;y<720;y+=40)disk(x,y,1,'#d8ddd3');
 text('FORM / FLOW',62,66,19,'#456159',800);text('INTERFACE STUDY 01',1218,66,16,'#456159',400,'right');
 text('One thought.',62,154,58,'#123d34',800);text('Many forms.',64,196,25,'#456159');
 const w=mix(310,760,open),h=mix(82,330,open),x=640-w/2,y=408-h/2;
 c.save();c.shadowColor='#21483a24';c.shadowBlur=45;c.shadowOffsetY=22;rect(x,y,w,h,mix(41,28,open),'#fffef8');c.restore();
 c.save();c.globalAlpha=1-smooth(board*3);disk(x+43,y+41,18,'#ee754f');line([[x+36,y+41],[x+50,y+41]],'#fffef8',3);line([[x+43,y+34],[x+43,y+48]],'#fffef8',3);text('A new idea',x+78,y+49,23,'#123d34',800);c.restore();
 c.save();c.globalAlpha=smooth((open-.92)/.08)*(1-smooth(board*3));text('Make room for the next move.',x+35,y+112,24,'#456159');rect(x+35,y+142,w-70,2,1,'#e8ebe2');text('A small collection of possibilities',x+35,y+186,18,'#456159');rect(x+35,y+h-85,180,48,24,'#c8edc8');text('Start shaping',x+58,y+h-54,17,'#123d34',800);disk(x+w-60,y+h-61,21,'#123d34');line([[x+w-67,y+h-61],[x+w-53,y+h-61],[x+w-59,y+h-67]],'#ffffff',2);c.restore();
 for(let i=0;i<3;i++){
  const bx=mix(x+35,252+i*265,board),by=mix(y+142,276,board),bw=mix(w-70,246,board),bh=mix(2,279,board);
  c.save();c.globalAlpha=board;rect(bx,by,bw,bh,19,['#c8edc8','#ffe1b4','#dcd9f2'][i]);c.globalAlpha=smooth((board-.82)/.18);text(['Capture','Arrange','Focus'][i],bx+23,by+41,22,'#123d34',800);
  for(let j=0;j<2;j++){rect(bx+16,by+64+j*93,bw-32,76,12,'#fffef8');disk(bx+35,by+86+j*93,5,['#55a978','#ee754f','#8e83bf'][i]);text([['Keep the spark','Ask one question'],['Group the pieces','Find a direction'],['Choose one move','Give it space']][i][j],bx+22,by+117+j*93,15,'#456159');}c.restore();
 }
 const orbit=2*Math.PI*t/9;disk(640+460*Math.cos(orbit),408+132*Math.sin(orbit),7,'#ee754f');
 text('CAPTURE',365,650,16,'#456159',800,'center');text('ARRANGE',640,650,16,'#456159',800,'center');text('FOCUS',915,650,16,'#456159',800,'center');line([[450,644],[546,644]],'#b7c5b9',2);line([[735,644],[826,644]],'#b7c5b9',2);
};})();
