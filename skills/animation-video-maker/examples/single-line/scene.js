(() => {
'use strict';
const C=A.ctx,ink='#243b49',paper='#f8faf7';
// One uninterrupted authored path. Repeated corners describe systems;
// the connector never breaks while old and new structures coexist.
const path=[[125,748],[225,748],[225,580],[280,580],[280,500],[440,500],[440,580],[495,580],[495,748],[225,748],[225,640],[495,640],[495,748],[620,748],[620,690],[675,690],[675,590],[745,590],[745,690],[805,690],[805,748],[900,748],[900,460],[1090,460],[1090,748],[900,748],[900,540],[1090,540],[1090,620],[900,620],[900,748],[1190,748],[1190,660],[1250,660],[1250,555],[1320,555],[1320,660],[1390,660],[1390,748],[1470,748],[1470,505],[1695,505],[1695,748],[1470,748],[1470,580],[1695,580],[1695,655],[1470,655],[1470,748],[1790,748]];
window.scene=t=>{
 A.frame(paper,false,'CONNECTION WITHOUT A RECKLESS REWRITE');
 const stage=t<5?0:t<10?1:2;
 A.text(['The future still has to','Modernize in','Preserve traceability.'][stage],100,290,70,ink,800);
 A.text(['connect to today.','visible increments.','Design for resilience.'][stage],100,380,70,ink,800);
 C.save();C.strokeStyle='#e4e9e5';C.lineWidth=1;for(let y=480;y<800;y+=40){C.beginPath();C.moveTo(104,y);C.lineTo(1810,y);C.stroke();}C.restore();
 const p=.09+.91*A.ease(t/12);
 A.line(path,A.blue,6,p);
 // Subordinate leader ticks identify concepts, not separate network edges.
 [['Legacy systems',360],['APIs & data',995],['Operations',1580]].forEach(([s,x],i)=>{if(t>=i*2){A.text(s,x,835,34,ink,400,'center');}});
 A.text(['Incremental modernization for critical operations.','Reliable contracts, pipelines and visibility.','Offline-first and recovery-aware designs.'][stage],104,922,34,ink);
};
window.TRANSCRIPT='The future still has to connect to today. T2S Modernization and Integration provides incremental modernization for legacy platforms, APIs, data flows, partner integrations and critical operations. Modernize in visible increments, with reliable contracts, pipelines and visibility. Preserve traceability and control. Design for resilience with offline-first and recovery-aware approaches. Evidence before expansion. Start a technical conversation at t2stech.com/contact.';
})();
