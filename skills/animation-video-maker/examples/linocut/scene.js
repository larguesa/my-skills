(() => {
'use strict';
const {ctx:c}=A,INK='#233832',PAPER='#e8dfc9',RUST='#b44f32';
function mass(points,color=INK){c.fillStyle=color;c.beginPath();points.forEach((v,i)=>i?c.lineTo(...v):c.moveTo(...v));c.closePath();c.fill();}
function tower(x,y,w,h){mass([[x,y],[x+w-5,y-8],[x+w,y+h],[x-5,y+h]]);for(let i=0;i<w-14;i+=17)A.line([[x+i+9,y+20],[x+i+5,y+h-12]],PAPER,3);}
window.TRANSCRIPT='The future still has to connect to today. Incremental modernization connects legacy platforms, APIs and data flows. Reliable contracts support the connection. Traceability and control remain part of the work. T2S Tech: start a technical conversation. This is an original procedural linocut-inspired illustration. Evidence before expansion. Start a technical conversation at t2stech.com/contact. Software that matters.';
window.scene=t=>{
 A.frame(PAPER,false,'KEEP THE CONNECTION');
 A.text('Modernize the connection.',110,284,70,INK,800);
 A.text('The future still has to connect to today.',112,352,37,INK);
 // Relief-print bridge: white gouges remove ink, not pencil outlines.
 tower(170,532,180,278);tower(1514,496,195,314);
 let p=A.ease((t-.8)/2);c.save();c.beginPath();c.rect(345,395,1175*p,450);c.clip();
 mass([[320,699],[440,699],[631,476],[1254,476],[1439,699],[1544,699],[1544,750],[1408,750],[1227,533],[654,533],[459,750],[320,750]]);
 for(let i=0;i<35;i++){let x=450+i*28;A.line([[x,497],[x+20,514]],PAPER,4);}
 for(let i=0;i<9;i++){let x=668+i*64;mass([[x,534],[x+14,534],[x+14,703],[x,703]]);}
 mass([[320,696],[1545,696],[1545,751],[320,751]],RUST);
 for(let i=0;i<46;i++){let x=327+i*26;A.line([[x,724],[x+18,711]],PAPER,2);}
 c.restore();
 A.text('Legacy platforms',260,872,32,INK,800,'center');A.text('New integrations',1600,872,32,INK,800,'center');
 if(t>4){let q=A.ease((t-4)/.6);c.save();c.globalAlpha=q;A.text('APIs + data flows',960,428,40,INK,800,'center');c.restore();}
 if(t>8){let q=A.ease((t-8)/.6);c.save();c.globalAlpha=q;A.text('Reliable contracts',960,825,38,INK,800,'center');c.restore();}
 if(t>12){let q=A.ease((t-12)/.6);c.save();c.globalAlpha=q;A.text('Traceability + control',960,901,37,RUST,800,'center');c.restore();}
 // Fixed ink speckles remain inside the illustration field.
 c.fillStyle=PAPER;for(let i=0;i<330;i++){let x=175+(i*137%1530),y=490+(i*79%320);if((x<340||x>1520))c.fillRect(x,y,2+i%3,2);}
};
})();