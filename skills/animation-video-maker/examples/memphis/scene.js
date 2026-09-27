(() => {
'use strict';
const C=A.ctx, navy='#20284c',pink='#f07c98',yellow='#f4ca51',cream='#fff6e6';
function disk(x,y,r,color){C.fillStyle=color;C.beginPath();C.arc(x,y,r,0,Math.PI*2);C.fill();}
function zig(x,y,w,h,color){const pts=[];for(let i=0;i<9;i++)pts.push([x+i*w/8,y+(i%2)*h]);A.line(pts,color,9);}
function shape(x,y,kind,rotation){C.save();C.translate(x,y);C.rotate(rotation);if(kind===0){disk(0,0,92,pink);disk(0,0,44,cream);}else if(kind===1){C.fillStyle=yellow;C.fillRect(-80,-80,160,160);for(let k=-48;k<70;k+=32)A.line([[-62,k],[62,k]],navy,5);}else{C.fillStyle=A.blue;C.beginPath();C.moveTo(0,-106);C.lineTo(103,78);C.lineTo(-103,78);C.closePath();C.fill();}C.restore();}
window.scene=t=>{
 A.frame(cream,false,'CONTINUOUS ENGINEERING');
 const stage=t<5?0:t<10?1:2;
 const titles=['The first release','Keep the work','Evolve with'];
 const sub=['is a beginning.','moving.','real feedback.'];
 A.text(titles[stage],100,300,76,navy,800);A.text(sub[stage],100,395,76,navy,800);
 const lines=[['Corrections. Improvements.','New integrations.'],['Prioritize value, urgency','and evidence.'],['New capability, shaped by feedback.','Documentation, tests and debt control.']][stage];
 A.text(lines[0],104,487,36,navy);A.text(lines[1],104,541,36,navy);
 // An asymmetric kinetic sculpture: independent pieces become a loop.
 const phase=A.ease((t-stage*5)/1.4),cx=1370,cy=525;
 C.save();C.strokeStyle=navy;C.lineWidth=9;C.beginPath();C.ellipse(cx,cy,275,234,0,0,Math.PI*2);C.stroke();C.restore();
 const labels=['Backlog','Reliability','Improvement'];
 for(let i=0;i<3;i++){
  const theta=-Math.PI/2+i*2*Math.PI/3+(stage===1?phase*.32:0);
  const x=cx+Math.cos(theta)*275,y=cy+Math.sin(theta)*234;
  shape(x,y,i,(i===1?-.12:.08)*Math.sin(t*1.3+i));
 }
 zig(108,660,420,32,A.blue);disk(610,684,22,pink);
 C.fillStyle=yellow;C.fillRect(104,760,650,95);A.text(labels[stage],135,824,44,navy,800);
 for(let x=1110;x<=1670;x+=40)for(let y=832;y<=892;y+=30)disk(x,y,4,navy);
 A.text('Recurring engineering capacity',1030,795,34,navy);
};
window.TRANSCRIPT='The first release is a beginning. Managed Evolution provides recurring engineering capacity for corrections, improvements and new integrations. Prioritize backlog around value, urgency and evidence. Shape new capability with real feedback, with documentation, tests and technical debt control. Evidence before expansion. Start a technical conversation at t2stech.com/contact.';
})();
