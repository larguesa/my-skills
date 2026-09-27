/* Original marker paths, revealed by physical path length. */
(()=>{'use strict';
const C=A.ctx;
function stroke(points,start,t,color=A.ink,width=6,duration=1.5){if(t<=start)return;A.line(points,color,width,A.ease((t-start)/duration));}
function loop(x,y,rx,ry){return Array.from({length:65},(_,i)=>{let a=i/64*Math.PI*2;return[x+Math.cos(a)*(rx+Math.sin(i*2.1)*1.4),y+Math.sin(a)*(ry+Math.cos(i*1.7)*1.2)];});}
function arrow(x,y,t,start){stroke([[x,y],[x+160,y-3]],start,t,A.blue,6,.8);stroke([[x+138,y-23],[x+160,y-3],[x+137,y+18]],start+.6,t,A.blue,6,.4);}
window.TRANSCRIPT='Make the hard problem legible. T2S AI-First Discovery starts with the problem and its constraints, shapes a value hypothesis with testable success criteria, and develops a working prototype. Bring the evidence into a pilot plan: backlog, capacity and the next decision. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame('#fbfaf5',false,'DRAW THE REASONING');
 A.text('Make the hard problem legible.',100,284,65,A.ink,800);
 // Permanent paper flecks do not crawl between exported frames.
 C.fillStyle='#e8e5dc';for(let i=0;i<230;i++)C.fillRect(110+(i*337%1690),330+(i*181%575),1.4,1.4);
 // Problem: a tangled but bounded map. The labels are not part of the scribble.
 stroke(loop(380,548,172,126),.15,t,A.ink,6,1.5);
 stroke([[264,523],[352,472],[451,580],[340,620],[328,509],[477,531],[402,607]],1.2,t,A.ink,5,1.8);
 for(let i=0;i<3;i++)stroke(loop(300+i*80,480+i*42,11,11),2+i*.18,t,A.blue,6,.35);
 A.text('Problem map',380,737,38,A.ink,800,'center');
 A.text('Context + constraints',380,788,31,A.ink,400,'center');
 arrow(590,545,t,4.6);
 // Hypothesis: a test tube and clearly named testable criterion, not a success stamp.
 if(t>=5){
  stroke([[918,425],[918,565],[873,642],[1036,642],[991,565],[991,425]],5,t,A.ink,6,1.8);
  stroke([[901,425],[1009,425]],5.8,t,A.ink,6,.5);
  stroke([[901,601],[1010,601]],6.5,t,A.blue,6,.7);
  stroke(loop(946,552,12,12),7,t,A.blue,5,.5);stroke(loop(972,518,8,8),7.4,t,A.blue,5,.4);
  A.text('Value hypothesis',955,737,38,A.ink,800,'center');A.text('Testable success criteria',955,788,31,A.ink,400,'center');
 }
 arrow(1175,545,t,9.5);
 // Prototype: browser on a stand, with only schematic UI geometry.
 if(t>=10){
  stroke([[1420,443],[1710,447],[1705,627],[1416,625],[1420,443]],10,t,A.ink,6,1.6);
  stroke([[1420,479],[1708,481]],10.8,t,A.ink,4,.5);
  stroke([[1558,629],[1558,660],[1485,662],[1632,662]],11.3,t,A.ink,6,.8);
  stroke([[1460,582],[1506,532],[1552,582],[1605,532],[1660,581]],11.6,t,A.blue,6,1.2);
  A.text('Working prototype',1565,737,38,A.ink,800,'center');A.text('A navigable or technical proof',1565,788,30,A.ink,400,'center');
 }
 if(t<13){A.text('Start with what needs to change.',100,904,36,A.blue,800);}
 else{
  stroke([[119,828],[122,850],[1790,850],[1792,828]],13,t,A.blue,5,1);
  A.text('Pilot plan: backlog, capacity and the next decision.',100,915,38,A.blue,800);
 }
};
})();
