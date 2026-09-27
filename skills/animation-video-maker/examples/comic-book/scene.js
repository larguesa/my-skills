/* Original three-panel editorial comic, not a licensed character style. */
(()=>{'use strict';
const C=A.ctx,paper='#f5eedc',black='#202a32',gold='#f2c94c';
function poly(p,fill,stroke=black,width=5){C.beginPath();p.forEach((v,i)=>i?C.lineTo(...v):C.moveTo(...v));C.closePath();C.fillStyle=fill;C.fill();C.strokeStyle=stroke;C.lineWidth=width;C.stroke();}
function circle(x,y,r,fill,width=5){C.beginPath();C.arc(x,y,r,0,Math.PI*2);C.fillStyle=fill;C.fill();C.strokeStyle=black;C.lineWidth=width;C.stroke();}
function burst(x,y,r){return Array.from({length:24},(_,i)=>{let a=i*Math.PI/12,rr=i%2?r*.79:r;return[x+Math.cos(a)*rr,y+Math.sin(a)*rr];});}
window.TRANSCRIPT='Agents can increase output. They cannot own the consequences. T2S AI Quality and Reliability brings testing, agent evaluation and security into delivery, with human review and release evidence for sensitive changes. Original illustrative comic; no actual release or measured result is depicted. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame(paper,false,'AN ILLUSTRATED QUALITY STORY');
 A.text('Output is not accountability.',100,280,65,black,800);
 const panels=[[[110,330],[630,330],[605,839],[110,839]],[[657,330],[1217,330],[1186,839],[630,839]],[[1244,330],[1810,330],[1810,839],[1213,839]]];
 panels.forEach((p,i)=>{
  const visible=t>=i*5;poly(p,visible?[gold,'#dce8fa','#d7ece9'][i]:'#e6dfcf');
  if(!visible)return;
  C.save();C.beginPath();p.forEach((v,j)=>j?C.lineTo(...v):C.moveTo(...v));C.closePath();C.clip();
  // Halftone ink is locked to each panel, not screen-noise animation.
  C.fillStyle='rgba(32,42,50,.11)';for(let x=120+i*580;x<690+i*580;x+=20)for(let y=347;y<698;y+=20){C.beginPath();C.arc(x,y,2.2,0,Math.PI*2);C.fill();}
  const e=A.ease((t-i*5)/1.1);
  C.save();C.translate(0,32*(1-e));
  if(i===0){
   C.save();C.translate(355,560);C.scale(.72,.72);C.translate(-355,-530);
   poly(burst(355,530,178),paper);
   // Pages flying from an abstract machine: increased output, not a robot person.
   for(let j=2;j>=0;j--)poly([[260+j*33,431-j*24],[420+j*33,431-j*24],[420+j*33,590-j*24],[260+j*33,590-j*24]],'#ffffff');
   A.line([[286,487],[315,469],[286,451]],A.blue,7);A.line([[369,451],[340,469],[369,487]],A.blue,7);
   poly([[249,590],[473,590],[494,653],[226,653]],black);
   C.restore();
   A.text('MORE OUTPUT',359,391,31,black,800,'center');
  }else if(i===1){
   poly([[775,421],[1030,421],[1030,648],[775,648]],paper);
   for(let j=0;j<4;j++)A.line([[803,464+j*44],[969,464+j*44]],black,5);
   circle(997,515,92,'#d8f3f9',8);
   A.line([[1058,582],[1134,664]],black,24);
   A.line([[960,515],[988,541],[1035,482]],A.blue,9);
   A.text('EXAMINE THE WORK',936,391,31,black,800,'center');
  }else{
   // Reviewer silhouette, evidence folder and a decision desk.
   circle(1455,472,44,paper,6);
   poly([[1398,538],[1440,520],[1475,520],[1520,546],[1537,642],[1380,642]],A.blue);
   A.line([[1500,565],[1574,611]],black,14);
   poly([[1570,553],[1699,553],[1732,646],[1590,646]],paper);
   A.line([[1604,586],[1682,586]],black,5);A.line([[1614,614],[1690,614]],black,5);
   A.line([[1330,660],[1740,660]],black,12);
   A.text('KEEP PEOPLE IN CHARGE',1510,391,30,black,800,'center');
  }
  C.restore();
  C.fillStyle=paper;C.fillRect(100+i*580,704,580,135);
  A.text(['Agents can create.','Tests. Evaluation.','Human review.'][i], [139,684,1281][i],759,38,black,800);
  A.text(['Consequences remain.','Security checks.','Release evidence.'][i],[139,684,1281][i],807,33,black);
  C.restore();poly(p,'rgba(0,0,0,0)');
 });
 A.text(t<10?'Quality belongs inside delivery.':'Responsibility stays visible.',108,918,40,A.blue,800);
};
})();
