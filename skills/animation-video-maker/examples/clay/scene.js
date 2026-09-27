(() => {
'use strict';
const {ctx:c}=A;
function lump(x,y,w,h,color,tilt=0){c.save();c.translate(x,y);c.rotate(tilt);c.shadowColor='#43382a35';c.shadowBlur=25;c.shadowOffsetY=18;const g=c.createLinearGradient(-w/2,-h/2,w/2,h/2);g.addColorStop(0,'#ffffff');g.addColorStop(.08,color);g.addColorStop(.8,color);g.addColorStop(1,'#766e69');c.fillStyle=g;c.beginPath();c.roundRect(-w/2,-h/2,w,h,Math.min(w,h)*.3);c.fill();c.shadowBlur=0;c.shadowOffsetY=0;c.strokeStyle='#ffffff38';c.lineWidth=3;c.beginPath();c.roundRect(-w/2+13,-h/2+13,w-26,h-26,Math.min(w,h)*.24);c.stroke();c.restore();}
window.TRANSCRIPT='The first release is a beginning. Managed Evolution adds recurring engineering capacity for corrections, improvements and new integrations. Prioritize the backlog around value, urgency and evidence. Keep documentation, tests and technical debt in view. Start a technical conversation with T2S Tech. The tactile objects are procedural clay-inspired graphics, not photographed stop-motion. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame('#ece5db',false,'SHAPE WHAT COMES NEXT');
 const s=Math.floor(t*12)/12;
 A.text('A system keeps evolving.',110,284,70,'#3d4246',800);
 A.text('Recurring engineering capacity',112,350,38,'#63615d');
 // A kneaded modular sculpture on a quiet studio surface.
 c.fillStyle='#d2c7b9';c.beginPath();c.ellipse(1275,835,455,54,0,0,Math.PI*2);c.fill();
 lump(1260,727,500,200,'#718d9c',-.018);
 const a=A.ease((s-2)/1.6);if(a){let y=530+(1-a)*-120;lump(1130,y,200,200,'#de9d68',-.08*(1-a));}
 const b=A.ease((s-6)/1.6);if(b)lump(1384,530+(1-b)*-120,245,200,'#98af83',.12*(1-b));
 const d=A.ease((s-10)/1.6);if(d)lump(1270,401+(1-d)*-120,450,84,'#d3be87',-.05*(1-d));
 const labels=[['Correct','Respond to what needs attention.'],['Improve','Let feedback shape capability.'],['Connect','Keep integrations moving.']];
 labels.forEach((v,i)=>{let p=A.ease((s-i*4)/.6);if(!p)return;c.save();c.globalAlpha=p;lump(142,448+i*151,50,50,['#de9d68','#98af83','#718d9c'][i]);A.text(v[0],200,453+i*151,40,'#3d4246',800);A.text(v[1],200,500+i*151,31,'#63615d');c.restore();});
 A.text(t<12?'Release is the starting point.':'Stewardship: tests, documentation, technical debt.',110,914,36,'#454948');
};
})();