/* Original geometric composition: a problem becomes a bounded first move. */
(()=>{'use strict';
const C=A.ctx, paper='#f1edde',red='#d84b37',yellow='#edc642';
function disk(x,y,r,color){C.fillStyle=color;C.beginPath();C.arc(x,y,r,0,Math.PI*2);C.fill();}
function block(x,y,w,h,color){C.fillStyle=color;C.fillRect(x,y,w,h);}
window.TRANSCRIPT='Find the first move worth making. T2S AI-First Discovery connects a problem map, a testable value hypothesis and a working prototype to a pilot plan. Clarity is a deliverable. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame(paper,false,'GEOMETRIC STUDY');
 const phase=t<5?0:t<10?1:2,local=t-phase*5,p=A.ease(local/1.8);
 A.text(['Find the','Make the','Plan the'][phase],100,295,76,A.ink,800);
 A.text(['first move.','idea testable.','next decision.'][phase],100,380,76,A.ink,800);
 A.text(['An important problem.','A working prototype.','A credible path to production.'][phase],105,467,36);
 // The same three primitives change their relationship, not merely their colour.
 C.save();C.beginPath();C.rect(890,205,920,650);C.clip();
 if(phase===0){
  disk(1230,475,205,red);block(1320,380+130*(1-p),300,300,A.blue);
  C.save();C.translate(1200,610);C.rotate(-Math.PI/4*p);block(-200,-28,400,56,A.ink);C.restore();
  disk(1560,325,83,yellow);A.line([[980,780],[1740,780]],A.ink,4);
 }else if(phase===1){
  block(1000,290,660,410,A.ink);block(1020,310,620,370,paper);
  disk(1190,490,145,red);block(1345,345,240,290,A.blue);
  block(1030,707,600*p,28,yellow);
  A.line([[1140,510],[1190,555],[1260,440]],paper,13,p);
  A.line([[1425,455],[1480,490],[1425,525]],paper,9,p);
 }else{
  block(980,665,235,140,A.ink);block(1213,490,235,315,A.blue);block(1448,315,235,490,red);
  disk(1565,315,88,yellow);
  A.line([[1015,610],[1320,385],[1720,255]],A.ink,8,p);
  A.line([[1650,250],[1720,255],[1680,320]],A.ink,8,p);
 }
 C.restore();
 const labels=phase===0?['Problem map','Operating context']:phase===1?['Value hypothesis','Prototype']:['Pilot plan','Backlog · capacity · next decision'];
 block(105,570,10,173,phase===0?red:phase===1?A.blue:yellow);
 A.text(labels[0],145,625,38,A.ink,800);A.text(labels[1],145,692,32);
 A.line([[105,820],[780,820]],A.ink,3);
 A.text('CLARITY IS A DELIVERABLE',105,883,32,A.ink,800);
};
})();
