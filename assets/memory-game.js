class UnicornMemory {
  constructor(symbols, random = Math.random) {
    this.cards = [...symbols, ...symbols].map(symbol => ({ symbol, matched: false }));
    for (let i = this.cards.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [this.cards[i], this.cards[j]] = [this.cards[j], this.cards[i]];
    }
    this.open = []; this.moves = 0; this.pairs = 0;
  }
  choose(index) {
    if (!Number.isInteger(index) || !this.cards[index] || this.open.length === 2 || this.open.includes(index) || this.cards[index].matched) return 'ignored';
    this.open.push(index);
    if (this.open.length === 1) return 'first';
    this.moves++;
    if (this.cards[this.open[0]].symbol === this.cards[index].symbol) {
      this.open.forEach(i => { this.cards[i].matched = true; });
      this.open = []; this.pairs++; return 'match';
    }
    return 'miss';
  }
  turnBack() { if (this.open.length === 2) this.open = []; }
}
if (typeof module !== 'undefined') module.exports = { UnicornMemory };
if (typeof document !== 'undefined') {
  const board = document.getElementById('memory-board');
  const status = document.getElementById('memory-status');
  const restart = document.getElementById('memory-reset');
  const next = document.getElementById('memory-continue');
  const templates = [...document.querySelectorAll('[data-memory-symbol]')];
  let game, buttons;
  function paint() {
    game.cards.forEach((card, index) => {
      const shown = card.matched || game.open.includes(index);
      const button = buttons[index];
      button.classList.toggle('revealed', shown);
      button.classList.toggle('matched', card.matched);
      button.setAttribute('aria-label', `Card ${index + 1}: ${shown ? card.symbol + (card.matched ? ', matched' : ', revealed') : 'face down'}`);
      button.setAttribute('aria-disabled', String(card.matched || game.open.includes(index) || game.open.length === 2));
      button.querySelector('.memory-front').hidden = !shown;
      button.querySelector('.memory-back').hidden = shown;
    });
    document.getElementById('memory-moves').textContent = game.moves;
    document.getElementById('memory-pairs').textContent = game.pairs;
    next.hidden = game.open.length !== 2;
  }
  function start() {
    game = new UnicornMemory(templates.map(t => t.dataset.memorySymbol));
    board.replaceChildren();
    buttons = game.cards.map((card, index) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'memory-card';
      const back = document.createElement('span'); back.className = 'memory-back'; back.textContent = '✦'; back.setAttribute('aria-hidden','true');
      const front = document.createElement('span'); front.className = 'memory-front'; front.setAttribute('aria-hidden','true');
      front.append(templates.find(t => t.dataset.memorySymbol === card.symbol).content.cloneNode(true));
      const label = document.createElement('span'); label.className = 'memory-name'; label.textContent = card.symbol; front.append(label);
      button.append(back, front);
      button.addEventListener('click', () => {
        const outcome = game.choose(index); if (outcome === 'ignored') return;
        paint();
        status.textContent = outcome === 'first' ? `${card.symbol}. Choose another card.` : outcome === 'miss' ? 'Different pictures. Remember them, then select “Turn these cards back”.' : game.pairs === templates.length ? `You found all six pairs in ${game.moves} moves! Choose New game to play again.` : `A ${card.symbol} pair! ${game.pairs} of 6 pairs found.`;
        if (outcome === 'miss') next.focus();
      });
      board.append(button); return button;
    });
    paint(); restart.hidden = false; status.textContent = 'Ready! Choose any card to begin.';
  }
  next.addEventListener('click', () => { const first = game.open[0]; game.turnBack(); paint(); status.textContent = 'Choose two cards to try again.'; buttons[first].focus(); });
  restart.addEventListener('click', () => { start(); buttons[0].focus(); });
  start();
}
