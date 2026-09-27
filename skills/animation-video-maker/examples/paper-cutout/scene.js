(() => {
'use strict';
const {ctx:c}=A;
function paper(points,color,angle=0){c.save();c.rotate(angle);c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.closePath();c.shadowColor='#26373530';c.shadowBlur=16;c.shadowOffsetY=12;c.fillStyle=color;c.fill();c.shadowBlur=0;c.shadowOffsetY=0;c.strokeStyle='#ffffff55';c.lineWidth=2;c.stroke();c.restore();}
function leaf(x,y,r,color){c.save();c.translate(x,y);c.rotate(r);paper([[0,0],[18,-42],[83,-60],[106,-25],[75,6],[0,0]],color);c.restore();}
window.TRANSCRIPT='The first release is a beginning. Managed Evolution provides recurring engineering capacity. Prioritize the backlog around value, urgency and evidence. Improve capability through feedback. Maintain integrations, tests and technical debt control. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame('#f3efe5',false,'LAYER BY LAYER');
 // Fibres are fixed spatial marks, never animated noise.
 c.fillStyle='#7665450b';for(let i=0;i<850;i++){let x=96+(i*173%1728),y=190+(i*97%740);c.fillRect(x,y,2+(i%8),1);}
 A.text('Release is a beginning.',110,295,70,A.ink,800);
 A.text('Keep the system growing.',114,355,38,'#536257');
 const grow=A.ease((t-1)/2);c.save();c.translate(1230,835);
 paper([[-250,0],[240,0],[207,55],[-220,55]],'#ddd5bc');
 paper([[-85,-120],[85,-120],[61,0],[-60,0]],'#ca7854');
 c.save();c.scale(1,grow);paper([[-9,-120],[-13,-435],[5,-475],[11,-120]],'#3e6659');
 const leaves=[[-6,-220,3.3,'#577e64'],[6,-290,-.45,'#8fa877'],[-7,-355,3.3,'#426e5a'],[5,-420,-.6,'#a1b591']];
 leaves.forEach((v,i)=>{let q=A.ease((t-1.3-i*.55)/.9);c.save();c.translate(v[0],v[1]);c.scale(q,q);leaf(0,0,v[2],v[3]);c.restore();});c.restore();c.restore();
 const items=[['Prioritize','Value, urgency, evidence.'],['Improve','Capability shaped by feedback.'],['Steward','Tests, integrations, technical debt.']];
 items.forEach((v,i)=>{let q=A.ease((t-3-i*3.7)/.65);if(!q)return;c.save();c.translate(110+(1-q)*-140,405+i*150);c.globalAlpha=q;
 paper([[0,0],[680,3],[668,125],[7,120]],['#e5cf98','#cddfc7','#c7dce2'][i]);A.text(v[0],28,49,39,A.ink,800);A.text(v[1],28,95,31,A.ink);c.restore();});
 A.text('Recurring engineering capacity',1020,915,32,'#425a50');
};
})();