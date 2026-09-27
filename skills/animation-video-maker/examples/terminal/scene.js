(() => {
'use strict';
const C=A.ctx,bg='#0e1924',white='#e4efed',mint='#88d9b8',muted='#a1b5cb';
const rows=[['testing','generated, reviewed, regression-aware'],['agent evaluation','quality and behavior against real criteria'],['security','risk analysis and boundary checks'],['observability','cost, latency, failures and drift'],['release readiness','human review and release evidence']];
window.scene=t=>{
 A.frame(bg,true,'ILLUSTRATIVE TERMINAL · NOT LIVE OUTPUT');
 A.text(t<10?'Quality is not optional.':'Responsibility stays visible.',100,282,68,white,800);
 A.text('A quality system for AI-accelerated software.',104,352,36,muted);
 C.fillStyle='#172b39';C.fillRect(104,410,1712,480);C.strokeStyle='#466073';C.lineWidth=2;C.strokeRect(104,410,1712,480);
 C.fillStyle='#223b4b';C.fillRect(104,410,1712,65);
 A.text('EXPLANATORY PSEUDOCOMMAND: NOT EXECUTABLE',132,454,30,mint,400,'left','monospace');
 const cmd='$ explain quality --include human-review';
 A.text(cmd.slice(0,Math.min(cmd.length,Math.floor(t*30)+2)),140,534,35,white,400,'left','monospace');
 const n=Math.min(5,Math.max(0,Math.floor((t-1)/1.25)+1));
 for(let i=0;i<n;i++){
  const y=602+i*57,focus=t>=10?i===4:i===Math.min(4,Math.floor(t/2));
  if(focus){C.fillStyle='#294455';C.fillRect(124,y-38,1668,50);}
  A.text(rows[i][0],146,y,31,mint,400,'left','monospace');
  A.text(rows[i][1],510,y,31,white,400,'left','monospace');
 }
 A.text('Illustration only. No commands run. No test results claimed.',106,924,30,muted);
};
window.TRANSCRIPT='Illustrative terminal, not live output. The pseudocommand explains a service; it is not executable. AI Quality and Reliability covers testing, agent evaluation, security, observability and release readiness. Testing is generated, reviewed and regression-aware. Agent quality and behavior are measured against real criteria. Security includes risk analysis and boundary checks. Observability covers cost, latency, failures and drift. Sensitive changes require human review and release evidence. No commands run and no test results are claimed. Evidence before expansion. Start a technical conversation at t2stech.com/contact.';
})();
