(() => {
'use strict';
const C=A.ctx, paper='#f6e9c9',brown='#523324',orange='#c56536',mustard='#c39438',olive='#74794b';
window.scene=t=>{
 A.frame(paper,false,'CLARITY IS A DELIVERABLE');
 const stage=t<5?0:t<10?1:2;
 const head=[['Find the first','move worth','making.'],['From problem','to tested','hypothesis.'],['A credible','path to','production.']][stage];
 head.forEach((s,i)=>A.text(s,100,300+i*96,82,brown,800));
 const notes=[['A focused discovery engagement.','Start concrete. Stay bounded.'],['Problem map. Value hypothesis.','A working prototype.'],['System map. Pilot plan.','The next decision, made legible.']][stage];
 notes.forEach((s,i)=>A.text(s,104,650+i*54,35,brown));
 // Five parallel printed bands bend toward a single, open horizon.
 const colors=[brown,orange,mustard,olive,A.blue];
 colors.forEach((color,i)=>{
  const x=1050+i*91,r=425-i*91;
  C.save();C.strokeStyle=color;C.lineWidth=57;C.lineCap='round';
  const length=235+Math.PI*r/2+305,progress=.16+.84*A.ease((t-i*.16)/2.4);
  C.setLineDash([length,length]);C.lineDashOffset=length*(1-progress);
  C.beginPath();C.moveTo(x,895);C.lineTo(x,660);C.arc(1475,660,r,Math.PI,Math.PI*1.5);C.lineTo(1780,660-r);C.stroke();C.restore();
 });
 // Warm overprint dots are fixed mathematical texture, not archival film.
 C.save();C.globalAlpha=.12;C.fillStyle=brown;
 for(let i=0;i<1600;i++){const x=96+(i*193%1728),y=195+(i*89%728);C.fillRect(x,y,1.4,1.4);}C.restore();
 const u=A.ease((t-stage*5)/1.4);
 C.save();C.translate(1575,720);C.rotate(-.1+u*.1);C.fillStyle=paper;C.strokeStyle=brown;C.lineWidth=3;C.beginPath();C.arc(0,0,139,0,Math.PI*2);C.fill();C.stroke();
 A.text(['Problem','Prototype','Pilot'][stage],0,-5,39,brown,800,'center');A.text(['map','proof','plan'][stage],0,46,36,brown,400,'center');C.restore();
 A.text('Evidence before expansion.',104,858,38,brown,800);
};
window.TRANSCRIPT='AI-First Discovery: find the first move worth making. A focused engagement turns an important problem into a tested hypothesis, a working prototype and a credible path to production. Outputs include a problem map, value hypothesis, prototype, system map and pilot plan. Evidence before expansion. Start a technical conversation at t2stech.com/contact.';
})();
