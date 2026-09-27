(() => {
'use strict';
const C=A.ctx, grid=16, dark='#172a35',sky='#e1f1ef',leaf='#287c69',gold='#e1ac50';
function sprite(pattern,x,y,color,scale=grid){C.fillStyle=color;pattern.forEach((row,j)=>[...row].forEach((v,i)=>{if(v==='1')C.fillRect(x+i*scale,y+j*scale,scale,scale);}));}
const tree=['0001000','0011100','0111110','1111111','0011100','0001000','0001000'];
const house=['000111000','001111100','011111110','111111111','011111110','011001110','011001110'];
window.scene=t=>{
 A.frame(sky,false,'DISCRETE STEPS · CONTINUOUS CARE');
 const stage=t<5?0:t<10?1:2;
 A.text(['Release is only','Keep improving.','Care for what'][stage],100,285,72,dark,800);
 A.text(['the beginning.','Keep integrating.','comes next.'][stage],100,375,72,dark,800);
 A.text(['Recurring engineering capacity','New capability shaped by real feedback','Documentation, tests and technical debt control'][stage],104,448,36,dark);
 // Original tile landscape, not a copied game or a progress dashboard.
 C.fillStyle=dark;C.fillRect(112,784,1696,32);C.fillStyle=leaf;C.fillRect(112,768,1696,16);
 for(let x=112;x<1808;x+=64){C.fillStyle=x%128===48?'#b7c9b3':'#c8d9c3';C.fillRect(x,816,48,64);}
 const baseX=[240,800,1360];
 baseX.forEach((x,i)=>{
  const arrival=A.clamp((t-i*3)/1.2),y=656+Math.round((1-arrival)*7)*16;
  if(arrival>0){sprite(house,x,y,i===stage?A.blue:dark);sprite(tree,x+192,656,leaf);}
  C.fillStyle=i===stage?gold:'#c3d8d4';C.fillRect(x-16,520,416,72);
  A.text(['Corrections','Integrations','Stewardship'][i],x+8,569,32,dark,800);
 });
 const step=Math.min(82,Math.floor(t*6)),px=128+step*16;
 sprite(['0110','1111','0110','1111','1010'],px,688,gold);
 // Paper-like stepped delivery token, never a success badge or game score.
 C.fillStyle=gold;C.fillRect(px+16,672,32,16);
 A.text('Illustrative landscape · no performance metrics',110,925,30,dark);
};
window.TRANSCRIPT='The first release is a beginning. Managed Evolution supplies recurring engineering capacity for corrections, improvements and new integrations. New capability is shaped by real feedback. Stewardship includes documentation, tests and technical debt control. This pixel landscape is illustrative, not a performance dashboard. Evidence before expansion. Start a technical conversation at t2stech.com/contact.';
})();
