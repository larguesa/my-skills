/* Instrument grammar without invented metrics, logs or live telemetry. */
(()=>{'use strict';
const C=A.ctx,white='#e5f5ff',muted='#97afc5',dim='#25415a';
function arc(x,y,r,a,b,color,width=4){C.beginPath();C.arc(x,y,r,a,b);C.strokeStyle=color;C.lineWidth=width;C.stroke();}
function dot(x,y,r,color){C.beginPath();C.arc(x,y,r,0,Math.PI*2);C.fillStyle=color;C.fill();}
window.TRANSCRIPT='A control surface for software accelerated by AI. T2S AI Quality and Reliability covers testing, agent evaluation, security, observability and release readiness. Evaluate against real criteria. Observe cost, latency, failures and drift. Keep human review and evidence at sensitive changes. This interface is a conceptual illustration, not live telemetry. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame('#0b1928',true,'CONCEPT INTERFACE · NOT LIVE TELEMETRY');
 A.text('Quality has a control surface.',102,272,64,white,800);
 const phase=t<5?0:t<10?1:2,active=[1,3,4][phase],p=A.ease((t-phase*5)/1.8),cx=600,cy=585;
 // Segmented instrument: categories, deliberately without numeric scales.
 for(let i=0;i<5;i++){
  let start=-Math.PI/2+i*Math.PI*2/5+.07,end=start+Math.PI*2/5-.14;
  arc(cx,cy,207,start,end,dim,15);arc(cx,cy,207,start,start+(end-start)*(phase===0?p:1),i===active?A.cyan:A.blue,7);
 }
 arc(cx,cy,156,0,Math.PI*2,dim,2);
 for(let i=0;i<40;i++){
  let a=i*Math.PI/20,r=i%5===0?239:231;
  A.line([[cx+Math.cos(a)*223,cy+Math.sin(a)*223],[cx+Math.cos(a)*r,cy+Math.sin(a)*r]],i%5===0?muted:dim,2);
 }
 A.text('CONTROL',cx,576,40,white,800,'center');A.text('SURFACE',cx,625,40,white,800,'center');
 const names=[{label:'Testing',x:600,y:348,a:-Math.PI/2,align:'center'},
 {label:'Agent evaluation',x:872,y:486,a:-.35,align:'left'},
 {label:'Security',x:872,y:753,a:.63,align:'left'},
 {label:'Observability',x:326,y:753,a:2.5,align:'right'},
 {label:'Human review',x:326,y:486,a:3.49,align:'right'}];
 names.forEach((n,i)=>{let x=cx+Math.cos(n.a)*251,y=cy+Math.sin(n.a)*251;dot(x,y,6,i===active?A.cyan:muted);A.text(n.label,n.x,n.y,30,i===active?white:muted,400,n.align);});
 // Rectilinear framing contrasts with the circular overview.
 A.line([[1155,362],[1155,793]],dim,2);
 A.line([[1210,364],[1245,364]],A.cyan,5);
 A.text(['Evaluate.','Observe.','Review.'][phase],1210,444,64,white,800);
 const copy=[['Quality and behavior','against real criteria.'],['Cost and latency.','Failures and drift.'],['Human review.','Evidence for sensitive','changes.']][phase];
 copy.forEach((s,i)=>A.text(s,1210,523+i*53,34,muted));
 A.line([[1210,727],[1750,727]],dim,2);
 A.text(['Agent evaluation','Observability','Release readiness'][phase],1210,778,33,A.cyan,800);
 // No status words such as PASS, healthy or approved: this is a service diagram.
 A.line([[110,850],[1808,850]],dim,2);
 A.text('Illustrative controls. No measured system state.',112,914,34,muted);
};
})();
