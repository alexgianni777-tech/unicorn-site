const BINGO_WORDS = ['Unicorn','Rainbow','Star','Moon','Cloud','Sparkle','Castle','Crown','Wand','Wings','Flower','Heart','Crystal','Meadow','Cupcake','Ribbon','Balloon','Wish','Magic','Sunshine','Butterfly','Jewel','Dream','Friendship'];
function shuffleBingo(items) {
  const copy = [...items];
  for (let i=copy.length-1;i>0;i--) { const j=Math.floor(Math.random()*(i+1)); [copy[i],copy[j]]=[copy[j],copy[i]]; }
  return copy;
}
function createBingoCards(count) {
  if (!Number.isInteger(count)||count<1||count>12) throw new RangeError('Choose 1 to 12 players.');
  const cards=[], selections=new Set();
  while(cards.length<count) {
    const card=shuffleBingo(BINGO_WORDS).slice(0,16);
    const signature=[...card].sort().join('|');
    if(!selections.has(signature)){ cards.push(card); selections.add(signature); }
  }
  return cards;
}
if(typeof module!=='undefined') module.exports={BINGO_WORDS,shuffleBingo,createBingoCards};
if(typeof document!=='undefined') {
  const form=document.getElementById('bingo-form'), cardsNode=document.getElementById('bingo-cards');
  const print=document.getElementById('bingo-print'), host=document.getElementById('bingo-host'), call=document.getElementById('bingo-call');
  let deck=[],called=[];
  function generate(event) {
    if(event) event.preventDefault();
    if(!form.reportValidity()) return;
    const cards=createBingoCards(Number(document.getElementById('bingo-count').value));
    cardsNode.replaceChildren();
    cards.forEach((words,index)=>{
      const section=document.createElement('section'); section.className='bingo-card';
      const heading=document.createElement('h3');heading.textContent=`Unicorn Bingo · Card ${index+1}`;section.append(heading);
      const table=document.createElement('table');table.setAttribute('aria-label',`Bingo card ${index+1}`);
      for(let row=0;row<4;row++){const tr=document.createElement('tr');for(let col=0;col<4;col++){const td=document.createElement('td');td.textContent=words[row*4+col];tr.append(td);}table.append(tr);}
      section.append(table);cardsNode.append(section);
    });
    deck=shuffleBingo(BINGO_WORDS);called=[];call.disabled=false;host.hidden=false;print.hidden=false;
    document.getElementById('bingo-current').textContent='Ready for the first word.';
    document.getElementById('bingo-history').textContent='';
    document.getElementById('bingo-status').textContent=`${cards.length} different cards ready. Printing includes all cards and the host word list.`;
  }
  form.addEventListener('submit',generate);
  print.addEventListener('click',()=>window.print());
  call.addEventListener('click',()=>{
    if(!deck.length)return;
    const word=deck.pop();called.push(word);
    document.getElementById('bingo-current').textContent=`${word} (${called.length} of ${BINGO_WORDS.length})`;
    document.getElementById('bingo-history').textContent=`Called: ${called.join(', ')}`;
    if(!deck.length){call.disabled=true;document.getElementById('bingo-current').textContent+=' — All words called.';}
  });
  generate();
}
