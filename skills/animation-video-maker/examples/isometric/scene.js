/* Original spatial workshop: functional objects, not fixed team headcount. */
(()=>{'use strict';
const C=A.ctx;
function project(x,y,z=0){return[1320+(x-y)*.84,399+(x+y)*.40-z];}
function face(points,fill){C.beginPath();points.forEach((v,i)=>i?C.lineTo(...v):C.moveTo(...v));C.closePath();C.fillStyle=fill;C.fill();C.strokeStyle='#628199';C.lineWidth=1.4;C.stroke();}
function cube(x,y,z,w,d,h,palette){
 const p=(a,b,c)=>project(a,b,c),[roof,left,right]=palette;
 face([p(x,y+d,z),p(x+w,y+d,z),p(x+w,y+d,z+h),p(x,y+d,z+h)],left);
 face([p(x+w,y,z),p(x+w,y+d,z),p(x+w,y+d,z+h),p(x+w,y,z+h)],right);
 face([p(x,y,z+h),p(x+w,y,z+h),p(x+w,y+d,z+h),p(x,y+d,z+h)],roof);
}
const light=['#f9fcff','#b8cddd','#88a7bd'],blue=['#7faaff','#3264ff','#234ba9'],cyan=['#7ce1e9','#21adc0','#177b98'],gold=['#ffe3a1','#e6b95c','#b18436'];
function path(points,color,width=4){A.line(points.map(p=>project(...p)),color,width);}
window.TRANSCRIPT='A team shaped around the outcome. T2S AI-Native Delivery Pods combine experienced specialists, supervised agents and visible evidence of progress. Prototypers explore, builders implement, sweepers simplify, growers iterate and maintainers sustain mature systems. The right mix changes with the work. Human checkpoints review decisions, releases and high-impact actions. This role-based spatial model does not prescribe team size. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame('#edf3f7',false,'ROLE-BASED SPATIAL MODEL');
 const phase=t<5?0:t<10?1:2;
 A.text(['A team shaped','The mix changes.','Human checkpoints.'][phase],100,285,62,A.ink,800);
 if(phase===0)A.text('around the outcome.',100,362,62,A.ink,800);
 else A.text(['','Accountability stays.','Visible evidence.'][phase],100,362,60,A.ink,800);
 const lines=phase===0?['Prototyper: explore ideas.','Builder: implement validated work.']:phase===1?['Sweeper: simplify the system.','Grower: iterate on product fit.','Maintainer: sustain mature systems.']:['Review decisions and releases.','Supervise high-impact actions.','Specialists + supervised agents.'];
 lines.forEach((s,i)=>{C.fillStyle=i%2?A.cyan:A.blue;C.fillRect(105,474+i*79,9,35);A.text(s,135,505+i*79,32);});
 // Floor has thickness, contact shadows and spatial connections.
 cube(0,0,-23,570,500,23,light);
 for(let i=0;i<6;i++){path([[i*95,0,1],[i*95,500,1]],'#c8d8e4',1);path([[0,i*100,1],[570,i*100,1]],'#c8d8e4',1);}
 const stations=[{x:55,y:45,k:0},{x:260,y:40,k:1},{x:445,y:165,k:2},{x:45,y:330,k:3},{x:290,y:350,k:4}];
 stations.forEach(s=>{path([[s.x+50,s.y+45,2],[265,s.y+45,2],[265,265,2]],'#7fa5c9',4);});
 // A workpiece travels along a floor route, then holds for reading.
 const travel=A.ease((t-phase*5)/1.8),route=phase===0?[[130,130],[265,130]]:phase===1?[[485,270],[265,270]]:[[265,390],[265,320]];
 const tx=route[0][0]+(route[1][0]-route[0][0])*travel,ty=route[0][1]+(route[1][1]-route[0][1])*travel;
 cube(tx-12,ty-12,4,24,24,16,gold);
 // Review platform at the shared junction, not an automatic release gate.
 cube(205,205,1,126,116,13,gold);
 const objects=[...stations,{x:230,y:230,k:5}].sort((a,b)=>(a.x+a.y)-(b.x+b.y));
 objects.forEach(s=>{
  const settle=1-A.ease((t-s.k*.3)/1.4),lift=settle*52;
  // Consistent diagonal footprint anchors each station to the floor.
  face([project(s.x-4,s.y+5),project(s.x+114,s.y+5),project(s.x+114,s.y+104),project(s.x-4,s.y+104)],'rgba(63,95,122,.12)');
  if(s.k===5){
   cube(s.x,s.y,15+lift,60,50,50,gold);
   let p=project(s.x+30,s.y+25,110+lift);C.beginPath();C.arc(p[0],p[1],18,0,Math.PI*2);C.fillStyle='#cf915d';C.fill();
   return;
  }
  cube(s.x,s.y,7+lift,102,87,44,light);
  if(s.k===0){cube(s.x+15,s.y+10,51+lift,33,32,38,gold);cube(s.x+58,s.y+34,51+lift,25,27,61,cyan);}
  if(s.k===1){cube(s.x+14,s.y+25,51+lift,74,24,75,blue);path([[s.x+28,s.y+52,106+lift],[s.x+45,s.y+52,119+lift],[s.x+63,s.y+52,104+lift]],'#ffffff',4);}
  if(s.k===2){for(let j=0;j<3;j++)cube(s.x+15+j*24,s.y+24,51+lift,16,38,15+j*14,cyan);}
  if(s.k===3){cube(s.x+25,s.y+24,51+lift,51,40,10,gold);path([[s.x+50,s.y+43,64+lift],[s.x+50,s.y+43,128+lift]],'#2b857c',7);path([[s.x+50,s.y+43,97+lift],[s.x+26,s.y+43,115+lift]],'#2b857c',7);path([[s.x+50,s.y+43,110+lift],[s.x+72,s.y+43,129+lift]],'#2b857c',7);}
  if(s.k===4){cube(s.x+20,s.y+16,51+lift,65,48,71,blue);for(let j=0;j<3;j++)path([[s.x+30,s.y+65,68+j*17+lift],[s.x+74,s.y+65,68+j*17+lift]],'#b9e7ff',4);}
 });
 A.line([[104,808],[742,808]],'#bccfdd',2);
 A.text('Roles adapt to the work.',105,864,36,A.blue,800);
 A.text('Conceptual workshop · not team size',105,915,30,'#5e7488');
};
})();
