"""Practical, printable host guidance for the existing party planner."""


def render() -> str:
    return '''<section id="party-preparation" class="party-preparation">
<h2>Your unicorn birthday party checklist, from invitations to cleanup</h2>
<p>Use this as a starting plan for a small party at home. Adjust timings to your guests and venue. Tick each step as it is arranged; your choices stay on this page until you reload and are included when you print.</p>
<div class="prep-grid">
<article><h3>2–3 weeks before</h3>
<label><input type="checkbox"> Choose the date, venue, start and finish time, and spending limit.</label>
<label><input type="checkbox"> Send <a href="/tools/unicorn-birthday-invitations.html">printable unicorn invitations</a> with an RSVP date and contact details.</label>
<label><input type="checkbox"> Ask about food needs and whether accompanying adults will stay.</label></article>
<article><h3>1 week before</h3>
<label><input type="checkbox"> Update the guest count in the calculator and include adults who will eat.</label>
<label><input type="checkbox"> Choose one main activity and one quiet backup from our <a href="/tools/free-unicorn-games.html">free unicorn games</a>.</label>
<label><input type="checkbox"> Print the <a href="/tools/unicorn-party-games.html#bingo">bingo cards</a> or <a href="/tools/unicorn-treasure-hunt.html">treasure-hunt clues</a> and count the copies.</label></article>
<article><h3>The day before</h3>
<label><input type="checkbox"> Count plates, cups, napkins and serving utensils; use what you already own.</label>
<label><input type="checkbox"> Prepare a cake knife, candles if using them, and a place to serve food.</label>
<label><input type="checkbox"> Set out activity supplies, named favor bags if wanted, and a cleanup bag.</label></article>
<article><h3>Before guests arrive</h3>
<label><input type="checkbox"> Clear a play space and keep walkways free.</label>
<label><input type="checkbox"> Put a quiet arrival activity on the table.</label>
<label><input type="checkbox"> Agree who welcomes guests, runs games and handles food.</label></article>
</div>
<h2>Worked example: a unicorn party for 12 guests</h2>
<p>With 12 invited guests, 2 hosts and a 10% extra allowance, the calculator rounds 14 × 1.10 up to <strong>16 plates and 16 cups</strong>. At 8 items per pack, that means <strong>2 packs of plates and 2 packs of cups</strong>. Twelve favors need one 12-pack of bags. These are examples, not recommended pack sizes.</p>
<p>If everyone uses another plate for cake, allow a second set: 32 plates in total under the same assumptions. Add those extra tableware costs to your budget. Skip favor bags if you do not want take-home gifts; the calculator's favor count is optional in practice.</p>
<h3>What to reuse, print and buy</h3>
<ul><li><strong>Reuse:</strong> cups, tablecloths, serving bowls and decorations you already own.</li>
<li><strong>Print:</strong> invitations and one activity. Our printables are free; paper and ink still have a cost.</li>
<li><strong>Buy only the gaps:</strong> food, cake ingredients or a cake, and supplies you cannot borrow or reuse. Check individual item counts in mixed party sets.</li></ul>
<p>For cake portions and decorating ideas, open the <a href="/tools/birthday-cake-servings-calculator.html">unicorn cake guide</a>. For optional take-home treats, compare <a href="/guides/unicorn-party-favor-ideas.html">party favor ideas</a>.</p>
<h2>Planning questions</h2>
<h3>Can I plan a unicorn party without buying a themed kit?</h3>
<p>Yes. Use plain tableware, choose two or three colors you already have, and add a printed invitation or game to carry the theme. The checklist separates required supplies from optional decorations and favors.</p>
<h3>What if the guests are different ages?</h3>
<p>Choose activities for the youngest participants and check any product's age guidance. Older guests can help read clues or run bingo. Keep a quiet activity available so joining every game is optional.</p>
<h3>How do I save the plan as a PDF?</h3>
<p>Enter your guest counts and costs, tick your checklist, then select <strong>Print this plan</strong>. Choose your browser's Save as PDF option. The printed version hides shopping buttons and includes the calculated list and preparation checklist.</p>
</section>'''
