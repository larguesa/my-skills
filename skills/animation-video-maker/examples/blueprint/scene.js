/* Original technical section: boundaries, controls and a human gate. */
(()=>{'use strict';
const C=A.ctx,white='#eaf5ff',muted='#8fb4d2',grid='#203e62';
function path(points,t,start,width=3,color=white,duration=1.3){if(t<=start)return;A.line(points,color,width,A.ease((t-start)/duration));}
function box(x,y,w,h,t,start,color=white){path([[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]],t,start,3,color);}
function cross(x,y){A.line([[x-10,y],[x+10,y]],muted,2);A.line([[x,y-10],[x,y+10]],muted,2);}
window.TRANSCRIPT='Quality is part of delivery. T2S AI Quality and Reliability brings testing, agent evaluation, security and observability into the control surface. Release readiness includes human review and evidence for sensitive changes. This is a conceptual control diagram, not a deployed system. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame('#112b4b',true,'CONCEPTUAL CONTROL DIAGRAM');
 for(let x=96;x<1824;x+=40)A.line([[x,200],[x,930]],grid,1);
 for(let y=200;y<=930;y+=40)A.line([[96,y],[1824,y]],grid,1);
 A.text('Engineer the control surface.',115,295,62,white,800);
 A.text('Quality is part of delivery.',120,354,34,muted);
 // Drafting boundary: the visible perimeter is descriptive, not a security guarantee.
 C.save();C.setLineDash([12,10]);box(135,402,1225,397,t,.2,muted);C.restore();
 A.text('SOFTWARE ACCELERATED BY AI',163,450,30,muted,800);
 const stations=[{x:190,y:485,w:425,h:118,label:'Testing',sub:'Regression-aware',start:1},
 {x:805,y:485,w:495,h:118,label:'Agent evaluation',sub:'Real criteria',start:4},
 {x:190,y:647,w:425,h:118,label:'Security',sub:'Boundary checks',start:7},
 {x:805,y:647,w:495,h:118,label:'Observability',sub:'Failures and drift',start:9}];
 for(const s of stations){
  box(s.x,s.y,s.w,s.h,t,s.start);
  if(t>=s.start){A.text(s.label,s.x+20,s.y+47,35,white,800);A.text(s.sub,s.x+20,s.y+91,30,muted);}
 }
 path([[620,544],[710,544],[710,706],[798,706]],t,5,4,A.cyan);
 path([[710,544],[798,544]],t,5,4,A.cyan);
 path([[620,706],[710,706]],t,8,4,A.cyan);
 // Independent gate sits outside the system boundary, with a human symbol.
 box(1460,477,310,288,t,11,A.cyan);
 if(t>=11){
  C.beginPath();C.arc(1615,535,23,0,Math.PI*2);C.strokeStyle=white;C.lineWidth=4;C.stroke();
  path([[1575,601],[1575,584],[1595,568],[1635,568],[1655,584],[1655,601]],t,11.4,4);
  A.text('Human review',1615,656,33,white,800,'center');A.text('Release evidence',1615,704,30,muted,400,'center');
 }
 path([[1368,621],[1450,621]],t,11.8,5,A.cyan);
 path([[1434,609],[1450,621],[1434,633]],t,12.6,5,A.cyan);
 [[135,402],[1360,402],[135,799],[1360,799]].forEach(v=>cross(...v));
 A.line([[135,847],[1770,847]],muted,2);
 A.text(t<11?'Tests · evaluation · security · observability':'Sensitive changes need human review and evidence.',140,904,36,white,800);
};
})();
