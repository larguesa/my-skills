(() => {
'use strict';
const {ctx:c}=A;
function reveal(word,x,y,size,color,progress){c.save();c.beginPath();c.rect(x,y-size-10,1720,size+35);c.clip();A.text(word,x,y+(1-A.ease(progress))*(size+30),size,color,800);c.restore();}
window.TRANSCRIPT='Do not buy a bag of hours. Shape a team around the outcome. AI-Native Delivery Pods combine experienced specialists and supervised agents. Human checkpoints review decisions, releases and high-impact actions. The mix changes with the work. Accountability does not. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame('#122133',true,'WORDS WITH WEIGHT');
 if(t<5){
  A.text('Do not buy a',112,338,65,'#d3deea',800);
  reveal('BAG OF HOURS.',105,549,133,'#ffffff',t/.7);
  A.line([[113,504],[1480,504]],'#00b4e8',15,A.ease((t-1)/.65));
  reveal('Build around the outcome.',113,788,67,'#5edbff',(t-1.6)/.7);
 }else if(t<11){
  const q=t-5;reveal('EXPERIENCED',110,340,100,'#ffffff',q/.6);reveal('SPECIALISTS',110,460,100,'#ffffff',(q-.13)/.6);
  A.text('+',111,595,100,'#5edbff',800);
  reveal('SUPERVISED AGENTS',110,713,88,'#5edbff',(q-.5)/.7);
  A.text('Human checkpoints for high-impact actions.',115,866,42,'#d3deea');
 }else{
  let q=t-11;A.text('The mix changes.',112,321,65,'#c5d4e5',800);
  reveal('ACCOUNTABILITY',106,527,119,'#ffffff',q/.6);
  reveal('DOES NOT.',108,700,137,'#5edbff',(q-.25)/.7);
  A.line([[112,757],[1740,757]],'#3264ff',8,A.ease((q-.8)/.6));
  A.text('A team shaped around the outcome.',113,858,43,'#d3deea');
 }
};
})();