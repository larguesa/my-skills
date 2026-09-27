/* Original schematic documentary plates, not archival footage. */
(()=>{'use strict';
const C=A.ctx,ivory='#eee5cf',muted='#aeb8b6',warm='#d6b57c';
function rect(x,y,w,h,c){C.fillStyle=c;C.fillRect(x,y,w,h);}
function outline(x,y,w,h,c=ivory){C.strokeStyle=c;C.lineWidth=3;C.strokeRect(x,y,w,h);}
function rack(x,y,w,h){outline(x,y,w,h);for(let i=0;i<5;i++){outline(x+14,y+17+i*(h-30)/5,w-28,31,muted);rect(x+w-37,y+26+i*(h-30)/5,9,9,warm);}}
window.TRANSCRIPT='The future still has to connect to today. T2S Modernization and Integration works incrementally across legacy platforms, APIs and data flows. Reliable contracts, traceability and recovery-aware designs keep operating context in view. Original schematic imagery, not archival footage. Start a technical conversation at t2stech.com/contact.';
window.scene=function(t){
 A.frame('#151d22',true,'ORIGINAL SCHEMATIC FILM');
 const shot=t<5?0:t<10?1:2,p=A.ease((t-shot*5)/1.4);
 // Film gate and perforations stay within the creative region.
 rect(96,200,1728,578,'#0b1013');
 for(let y=217;y<750;y+=64){rect(111,y,20,35,ivory);rect(1790,y,20,35,ivory);}
 C.save();C.beginPath();C.rect(151,215,1618,544);C.clip();
 C.translate(960,480);C.scale(1+Math.min(5,t-shot*5)*.007,1+Math.min(5,t-shot*5)*.007);C.translate(-960,-480);
 rect(151,215,1618,544,'#263138');
 // A continuous baseline binds three editorial views of the operating system.
 A.line([[200,671],[1740,671]],muted,2);
 if(shot===0){
  for(let i=0;i<4;i++)rack(310+i*160,310,120,340);
  A.line([[1050,650],[1050,365],[1570,365]],warm,6,p);
  A.line([[1050,365],[1190,265],[1520,265]],ivory,4);
  A.line([[1330,265],[1330,525],[1530,525]],ivory,4);
  outline(1510,475,160,170);A.line([[1530,630],[1590,560],[1640,630]],warm,5);
  A.text('LEGACY PLATFORMS',315,725,32,ivory,800);A.text('OPERATING CONTEXT',1120,725,32,ivory,800);
 }else if(shot===1){
  rack(300,350,210,270);outline(830,330,300,300,warm);outline(1450,350,210,270);
  A.line([[530,477],[808,477]],warm,7,p);A.line([[1150,477],[1425,477]],warm,7,p);
  for(let i=0;i<3;i++){A.line([[879,395+i*67],[930,430+i*67],[1015,385+i*67]],ivory,5);}
  A.text('EXISTING SYSTEM',250,713,32,ivory,800);A.text('API CONTRACT',848,713,32,ivory,800);A.text('NEW CAPABILITY',1390,713,32,ivory,800);
 }else{
  // Three connected frames, an editorial contact strip rather than a dashboard.
  for(let i=0;i<3;i++){
   let x=280+i*520;outline(x,310,400,310,muted);
   if(i===0){rack(x+50,365,100,185);A.line([[x+185,480],[x+245,420],[x+330,480]],warm,7,p);}
   if(i===1){for(let j=0;j<3;j++){outline(x+65+j*80,380+j*20,150,150,warm);} }
   if(i===2){C.beginPath();C.arc(x+200,458,91,.3,Math.PI*1.85);C.strokeStyle=warm;C.lineWidth=8;C.stroke();A.line([[x+245,355],[x+284,401],[x+222,410]],warm,8);}
  }
  A.text('INCREMENTAL CHANGE',280,709,31,ivory,800);A.text('TRACEABILITY',800,709,31,ivory,800);A.text('RECOVERY-AWARE',1320,709,31,ivory,800);
 }
 // Quiet procedural grain: deterministic, capped opacity, no luminance flicker.
 C.fillStyle='rgba(238,229,207,.055)';for(let i=0;i<900;i++){let x=151+(i*79%1618),y=215+(i*137%544);C.fillRect(x,y,2,2);}
 C.restore();
 A.text(['The future connects to today.','Modernize the connections.','Change in visible increments.'][shot],100,859,60,ivory,800);
 A.text(['Legacy platforms · APIs · data flows','Reliable contracts, not a reckless rewrite.','Traceability and control remain in view.'][shot],104,919,33,muted);
};
})();
