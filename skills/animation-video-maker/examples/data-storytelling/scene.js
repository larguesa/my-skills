(() => {
'use strict';
const C=A.ctx,ink='#20334a',muted='#586d81';
const roles=[['Prototyper','Explore ideas and prototypes'],['Builder','Turn validated ideas into product'],['Sweeper','Simplify and optimize the system'],['Grower','Improve fit with the market'],['Maintainer','Keep mature systems reliable']];
window.scene=t=>{
 A.frame('#f4f7fa',false,'A CATEGORICAL VIEW · NOT PERFORMANCE DATA');
 A.text(t<10?'A team shaped around the outcome.':'The mix changes. Accountability stays.',100,277,64,ink,800);
 // The only quantity is a source-grounded count of role categories.
 A.text(String(roles.length),100,563,236,A.blue,800);
 A.text('ROLE',105,645,54,ink,800);A.text('CATEGORIES',105,710,54,ink,800);
 A.text('Not a fixed headcount.',108,794,32,muted);
 A.text('Not an allocation chart.',108,839,32,muted);
 const n=Math.min(5,Math.floor(t/1.05)+1);
 for(let i=0;i<5;i++){
  const y=408+i*86,active=i<n;
  C.fillStyle=active?'#ffffff':'#e7edf4';C.fillRect(690,y-44,1104,73);
  C.fillStyle=active?A.blue:'#bccbd9';C.beginPath();C.arc(722,y-8,9,0,Math.PI*2);C.fill();
  if(active){A.text(roles[i][0],751,y,35,ink,800);A.text(roles[i][1],1060,y,30,muted);}
 }
 // The bracket denotes shared human oversight; its length encodes no quantity.
 A.line([[669,362],[642,362],[642,790],[669,790]],A.blue,4,A.ease((t-5.5)/1.2));
 if(t>=6){C.fillStyle='#dce6fb';C.fillRect(690,833,1104,83);A.text('Human checkpoints',718,886,35,ink,800);A.text('Decisions · releases · high-impact actions',1130,885,30,ink);}
};
window.TRANSCRIPT='A team shaped around the outcome. T2S publishes five role categories for AI-Native Delivery Pods: Prototyper, Builder, Sweeper, Grower and Maintainer. This is a categorical view, not performance data, staffing headcount or allocation percentages. The right mix changes with the work. Human checkpoints review decisions, releases and high-impact actions. The mix changes; accountability stays. Evidence before expansion. Start a technical conversation at t2stech.com/contact.';
})();
