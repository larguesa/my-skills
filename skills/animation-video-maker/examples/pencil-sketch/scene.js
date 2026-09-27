(() => {
'use strict';
const {ctx:c}=A,G='#55534f';
function sketch(points,p=1,w=2){for(let k=0;k<3;k++)A.line(points.map((v,i)=>[v[0]+Math.sin(i*3+k*2)*1.7,v[1]+Math.cos(i*5+k)*1.7]),k?'#55534f35':G,k?1:w,p);}
function block(x,y,w,h,p){sketch([[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]],p,3);for(let i=0;i<w;i+=14)sketch([[x+i,y+h],[x+Math.min(w,i+42),y+h-38]],p,1);}
window.TRANSCRIPT='The future still has to connect to today. T2S Tech supports incremental modernization of legacy platforms, APIs and data flows. Decompose the change. Define reliable contracts. Preserve traceability and control. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame('#f5f2e9',false,'STUDY THE CONNECTIONS');
 c.fillStyle='#59534609';for(let i=0;i<1800;i++)c.fillRect(98+i*193%1720,192+i*73%730,1,1);
 A.text('The future connects to today.',110,280,65,G,800);
 A.text('Incremental modernization. Not a reckless rewrite.',113,344,35,G);
 // Architectural study: original system, adapter, then future capability.
 block(155,455,350,285,A.ease(t/2));
 sketch([[170,475],[490,475]],A.ease((t-.5)/1.2));
 for(let j=0;j<3;j++)block(194,510+j*64,271,45,A.ease((t-.7-j*.25)/1));
 A.text('Existing system',330,800,34,G,800,'center');
 const adapter=A.ease((t-4)/1.3);sketch([[525,586],[690,586]],adapter,3);
 block(710,505,340,167,adapter);if(adapter){c.save();c.globalAlpha=adapter;A.text('API contract',880,600,37,G,800,'center');c.restore();}
 sketch([[1070,586],[1225,586]],A.ease((t-7.7)/1.1),3);
 const future=A.ease((t-8.6)/1.5);block(1250,457,450,285,future);
 for(let i=0;i<3;i++)block(1290+i*128,512,94,160,future);
 if(future){c.save();c.globalAlpha=future;A.text('New capability',1475,800,34,G,800,'center');c.restore();}
 const message=t<4?'Understand what exists.':t<8?'Decompose the change.':t<12?'Connect APIs and data.':'Preserve traceability and control.';
 A.text(message,112,905,40,A.blue,800);
 if(t>=12){let p=A.ease((t-12)/1);sketch([[1710,751],[1728,837],[152,837],[135,751]],p);}
};
})();