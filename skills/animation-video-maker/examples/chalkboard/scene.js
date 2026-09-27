(() => {
'use strict';
const {ctx:c}=A,W='#e9eee3',Y='#e4ce7d';
function chalk(points,progress=1,color=W,width=4){A.line(points,color,width,progress);for(let j=0;j<3;j++)A.line(points.map((p,i)=>[p[0]+Math.sin(i*7+j)*2,p[1]+Math.cos(i*3+j)*2]),'#e9eee329',1,progress);}
window.TRANSCRIPT='Find the first move worth making. AI-First Discovery starts with the problem, constraints and stakeholders. Define a value hypothesis with testable success criteria. Build a prototype and a pilot plan. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame('#203c37',true,'MAKE THE PROBLEM LEGIBLE');
 c.fillStyle='#f8f3d80a';for(let i=0;i<2300;i++)c.fillRect(96+(i*179%1728),195+(i*107%730),i%4+1,1);
 A.text('Find the first move',110,281,73,W,800);A.text('worth making.',110,370,73,Y,800);
 chalk([[115,400],[830,403]],A.ease(t/1.4),Y,5);
 // A board lesson builds cumulatively, rather than swapping slides.
 const columns=[{x:130,label:'Problem',sub:'Context + constraints',time:.5},{x:735,label:'Hypothesis',sub:'Testable success criteria',time:4.8},{x:1340,label:'Prototype',sub:'A working proof',time:9.2}];
 columns.forEach((v,i)=>{let p=A.clamp((t-v.time)/1.4);if(!p)return;
 chalk([[v.x,494],[v.x+430,491],[v.x+438,684],[v.x-4,690],[v.x,494]],p);
 if(p>.3){c.save();c.globalAlpha=A.clamp((p-.3)*3);A.text(v.label,v.x+215,572,46,W,800,'center');A.text(v.sub,v.x+215,634,30,W,400,'center');c.restore();}
 if(i<2)chalk([[v.x+455,584],[v.x+562,584],[v.x+544,567],[v.x+562,584],[v.x+544,602]],A.clamp((t-v.time-2)/.7),Y,4);
 });
 if(t>12.5){let p=A.ease((t-12.5)/.8);chalk([[1548,714],[1548,788],[361,788],[361,822]],p,Y);c.save();c.globalAlpha=p;A.text('Pilot plan: backlog, capacity, next decision.',130,884,42,Y,800);c.restore();}
};
})();