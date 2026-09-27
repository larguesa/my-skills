(() => {
'use strict';
const {ctx:c}=A;
function disk(x,y,r,color){c.fillStyle=color;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();}
function tile(x,y,w,h,color,r=22){c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();}
function human(x,y,color){disk(x,y,35,'#e9b590');c.fillStyle=color;c.beginPath();c.arc(x,y+106,62,Math.PI,0);c.lineTo(x+62,y+133);c.lineTo(x-62,y+133);c.fill();}
window.TRANSCRIPT='A team shaped around the outcome. AI-Native Delivery Pods combine experienced specialists and supervised agents. The right mix changes with the work: prototype, build, improve and maintain. Human checkpoints review decisions and releases. These original schematic figures represent capabilities, not a fixed team size. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame('#eaf2f8',false,'CAPABILITY, CONNECTED');
 A.text('Shape the team around the work.',110,282,65,'#16394a',800);
 A.text('Experienced specialists + supervised agents',112,345,36,'#416371');
 // Original cutaway workshop: capabilities orbit a shared worktable.
 tile(825,495,690,246,'#bad8e0',110);tile(867,532,608,175,'#ffffff',80);
 const phase=A.ease(t/1.2);c.save();c.globalAlpha=phase;human(999,460,'#3066a3');human(1378,460,'#d58063');c.restore();
 tile(1115,560,135,95,'#24536b',20);disk(1156,601,9,'#75d8dc');disk(1212,601,9,'#75d8dc');A.line([[1155,632],[1215,632]],'#75d8dc',5);
 A.text('Shared outcome',1165,802,38,'#16394a',800,'center');
 const verbs=['Prototype','Build','Improve','Maintain'];
 verbs.forEach((v,i)=>{let q=A.ease((t-1-i*2.2)/.6);if(!q)return;let y=412+i*108;c.save();c.globalAlpha=q;tile(112+(1-q)*-45,y,448,81,['#ffe2a1','#c5e2d6','#d1ddf3','#f2d1c2'][i]);disk(150,y+40,12,'#24536b');A.text(v,185,y+54,37,'#16394a',800);c.restore();});
 A.line([[591,631],[741,631],[790,610]],'#6b94a4',5,A.ease((t-3)/1));
 if(t>=10){let p=A.ease((t-10)/.7);c.save();c.globalAlpha=p;tile(1560,482,242,232,'#24536b',30);A.line([[1605,550],[1635,580],[1695,525]],'#8ee0cc',9);A.text('Human',1681,637,32,'#ffffff',800,'center');A.text('review',1681,678,32,'#ffffff',800,'center');c.restore();A.line([[1486,630],[1533,630]],'#24536b',5,p);}
 A.text('The mix changes. Accountability does not.',110,913,39,'#16394a',800);
};
})();