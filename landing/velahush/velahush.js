/* ==========================================================================
   VelaHush landing — behaviour.

   A plain-JS port of the prototype's view model. The original ran as a
   Claude Design "Design Component" (an <x-dc> body plus a DCLogic class);
   this reproduces the same state and derived values with no runtime, so the
   page opens straight from disk.

   OFFER is the single place prices and terms live — it mirrors the design's
   editable props, so changing a number here changes it everywhere on the page.
   ========================================================================== */
(function () {
  'use strict';

  var OFFER = {
    brand: 'VelaHush',
    gunPrice: 49,
    bundlePrice: 59.90,
    refillPrice: 21,
    refillDiscount: 0.15,   // plan price = refill * (1 - discount)
    guaranteeDays: 30,
    warrantyDays: 90,
    reviewCount: 25089,
    showUrgency: true
  };

  var refillSub = OFFER.refillPrice * (1 - OFFER.refillDiscount);   // 17.85

  /* Prices print without a trailing .00 — "$49", but "$59.90". */
  function money(n) { return '$' + n.toFixed(2).replace(/\.00$/, ''); }

  /* Fulfilment estimate: today+5 to today+9. Replace with the real SLA. */
  function shipWindow() {
    var fmt = function (d) { return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); };
    var now = Date.now();
    return fmt(new Date(now + 5 * 864e5)) + '–' + fmt(new Date(now + 9 * 864e5));
  }

  var PLANS = [
    { title: 'Gun only', note: 'One unit, one pod included. Try it on the couch first.',
      price: OFFER.gunPrice, compare: OFFER.gunPrice * 1.6, badge: '' },
    { title: 'Gun + 3 refill pods', note: 'About four months of weekly use. Cheapest way to get pods.',
      price: OFFER.bundlePrice, compare: OFFER.gunPrice + OFFER.refillPrice, badge: 'Most popular', badgeAccent: true },
    { title: 'Gun + refill plan', note: '3 pods now, then 3 every 2 months at ' + money(refillSub) + '. Skip or cancel anytime.',
      price: OFFER.bundlePrice, compare: OFFER.gunPrice + OFFER.refillPrice, badge: 'Never run out' }
  ];

  var SCENTS = ['Lemon', 'Lavender', 'Peppermint', 'Fresh Linen'];

  var GALLERY = [
    { short: 'unit + box', src: 'assets/unit-box.jpg' },
    { short: 'refill pods', src: 'assets/refill-pods.jpg' },
    { short: 'misting a sofa', src: 'assets/misting-sofa.jpg' },
    { short: 'in hand, scale', src: 'assets/in-hand.jpg' },
    { short: 'dog on treated rug', src: 'assets/dog-rug.jpg' }
  ];

  var MARQUEE = [
    'Neutralizes at the source', 'Dry mist, no residue', 'Cordless & rechargeable',
    '30,000+ US homes', OFFER.warrantyDays + '-day warranty', 'Refills from ' + money(refillSub)
  ];

  /* Demo data. Before launch, feed this from a real recent-order source or
     drop the section — see README.md. */
  var ORDERS = [
    ['Columbus, OH', 'Gun + refill plan', '2 min ago'],
    ['Sarasota, FL', 'Gun + 3 pods', '9 min ago'],
    ['Boise, ID', 'Gun + 3 pods', '14 min ago'],
    ['Round Rock, TX', 'Gun only', '21 min ago'],
    ['Grand Rapids, MI', 'Gun + refill plan', '26 min ago']
  ];

  var FAQS = [
    ['Does it actually remove pet odor, or just cover it?',
     'It neutralizes. The mist carries odor-binding agents into fabric instead of laying fragrance on top, which is why the smell does not come back the same evening. Deep, set-in odor on older upholstery may want a second pass.'],
    ['Is it safe around cats, dogs and grandkids?',
     'Yes. Dye-free, fragrance-light, and the dry mist evaporates in seconds. Give the surface about a minute before pets settle back in — same as any fabric refresher.'],
    ['What smells does it handle?',
     'Wet dog, litter box, accidents on carpet, pet beds, couches, blankets, car seats, and the general background smell you have stopped noticing in your own home.'],
    ['How long does a charge and a pod last?',
     'A full charge covers roughly 40 rooms. One pod treats a typical living room about 25 times. Three pods are ' + money(OFFER.refillPrice) + ', or ' + money(refillSub) + ' on the plan.'],
    ['How does the refill plan work?',
     'Three pods ship every two months at 15% off, in the scent you picked. Every email has skip, change-scent, and cancel links — no phone call, no minimum number of deliveries.'],
    ['Shipping, returns and warranty?',
     'Free US shipping over $50, dispatched from California, arriving ' + shipWindow() + ' with tracking. ' + OFFER.guaranteeDays + ' days for a full refund (keep the pods) and a ' + OFFER.warrantyDays + '-day warranty on the motor and battery.']
  ];

  var state = { plan: 1, scent: 0, faq: 0, img: 0, added: false, tick: 0 };

  var $ = function (id) { return document.getElementById(id); };

  /* --- Build once ---------------------------------------------------------- */

  function buildPlans() {
    var host = $('plans');
    PLANS.forEach(function (p, i) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'vh-plan';
      btn.setAttribute('aria-pressed', String(i === state.plan));
      btn.innerHTML =
        '<span class="vh-plan__radio" aria-hidden="true"></span>' +
        '<span class="vh-plan__main">' +
          '<span class="vh-plan__row">' +
            '<span class="vh-plan__title"></span>' +
            (p.badge ? '<span class="vh-badge' + (p.badgeAccent ? ' vh-badge--accent' : '') + '"></span>' : '') +
          '</span>' +
          '<span class="vh-plan__note"></span>' +
        '</span>' +
        '<span class="vh-plan__prices">' +
          '<span class="vh-plan__price"></span>' +
          '<span class="vh-plan__compare"></span>' +
        '</span>';
      btn.querySelector('.vh-plan__title').textContent = p.title;
      btn.querySelector('.vh-plan__note').textContent = p.note;
      btn.querySelector('.vh-plan__price').textContent = money(p.price);
      btn.querySelector('.vh-plan__compare').textContent = money(p.compare);
      if (p.badge) btn.querySelector('.vh-badge').textContent = p.badge;
      btn.addEventListener('click', function () {
        state.plan = i;
        state.added = false;   // a changed plan invalidates the "added" feedback
        render();
      });
      host.appendChild(btn);
    });
  }

  function buildScents() {
    var host = $('scents');
    SCENTS.forEach(function (name, i) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'vh-chip';
      btn.textContent = name;
      btn.setAttribute('aria-pressed', String(i === state.scent));
      btn.addEventListener('click', function () { state.scent = i; render(); });
      host.appendChild(btn);
    });
  }

  function buildThumbs() {
    var host = $('thumbs');
    GALLERY.forEach(function (g, i) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'vh-thumb';
      btn.setAttribute('aria-pressed', String(i === state.img));
      btn.setAttribute('aria-label', g.short);
      var note = document.createElement('span');
      note.className = 'vh-thumb__note';
      note.textContent = g.short;
      btn.appendChild(note);
      var img = document.createElement('img');
      img.className = 'vh-thumb__img grayscale';
      img.alt = '';
      img.onerror = function () { img.remove(); };   // no photo yet → caption stays
      img.src = g.src;
      btn.appendChild(img);
      btn.addEventListener('click', function () { state.img = i; render(); });
      host.appendChild(btn);
    });
  }

  function buildMarquee() {
    var host = $('marquee');
    // Duplicated once, then translated -50%, so the loop is seamless.
    MARQUEE.concat(MARQUEE).forEach(function (text) {
      var span = document.createElement('span');
      span.className = 'vh-marquee__item';
      span.textContent = text;
      host.appendChild(span);
    });
  }

  function buildOrders() {
    var host = $('orders');
    ORDERS.forEach(function (o) {
      var row = document.createElement('div');
      row.className = 'vh-order';
      row.innerHTML =
        '<span class="vh-order__dot" aria-hidden="true"></span>' +
        '<span class="vh-order__city"></span>' +
        '<span class="vh-order__item"></span>' +
        '<span class="vh-order__ago"></span>';
      row.querySelector('.vh-order__city').textContent = o[0];
      row.querySelector('.vh-order__item').textContent = o[1];
      row.querySelector('.vh-order__ago').textContent = o[2];
      host.appendChild(row);
    });
  }

  function buildFaq() {
    var host = $('faq-list');
    FAQS.forEach(function (f, i) {
      var item = document.createElement('div');
      item.className = 'vh-faq__item';
      var id = 'faq-panel-' + i;
      item.innerHTML =
        '<button class="vh-faq__q" type="button" aria-expanded="false" aria-controls="' + id + '">' +
          '<span></span><span class="vh-faq__sign" aria-hidden="true">+</span>' +
        '</button>' +
        '<div id="' + id + '" hidden><p class="vh-faq__a"></p></div>';
      item.querySelector('.vh-faq__q span').textContent = f[0];
      item.querySelector('.vh-faq__a').textContent = f[1];
      item.querySelector('.vh-faq__q').addEventListener('click', function () {
        state.faq = (state.faq === i) ? -1 : i;   // single-open; clicking the open row closes it
        render();
      });
      host.appendChild(item);
    });
  }

  /* --- Render -------------------------------------------------------------- */

  function render() {
    var plan = PLANS[state.plan];
    var summary = plan.title + ' · ' + SCENTS[state.scent] + ' · ' + money(plan.price);

    document.querySelectorAll('#plans .vh-plan').forEach(function (el, i) {
      el.setAttribute('aria-pressed', String(i === state.plan));
    });
    document.querySelectorAll('#scents .vh-chip').forEach(function (el, i) {
      el.setAttribute('aria-pressed', String(i === state.scent));
    });
    document.querySelectorAll('#thumbs .vh-thumb').forEach(function (el, i) {
      el.setAttribute('aria-pressed', String(i === state.img));
    });

    $('plan-note').textContent = state.plan === 2
      ? 'Plan billed ' + money(refillSub) + ' every 2 months after today. Skip or cancel in one click.'
      : 'One-time purchase. Add pods later at ' + money(OFFER.refillPrice) + ' for three.';

    var shot = GALLERY[state.img];
    $('hero-note').textContent = 'photo: ' + shot.short;
    var heroImg = $('hero-img');
    if (heroImg) {
      heroImg.onerror = function () { heroImg.style.display = 'none'; };
      heroImg.style.display = '';
      heroImg.src = shot.src;
    }

    $('cta-label').textContent = state.added ? 'Added to cart' : 'Add to cart';
    $('cta-price').textContent = state.added ? '✓' : money(plan.price);
    $('sticky-cta').textContent = state.added ? 'Added ✓' : 'Add — ' + money(plan.price);
    $('sticky-summary').textContent = summary;

    document.querySelectorAll('#faq-list .vh-faq__item').forEach(function (item, i) {
      var open = i === state.faq;
      item.querySelector('.vh-faq__q').setAttribute('aria-expanded', String(open));
      item.querySelector('.vh-faq__sign').textContent = open ? '–' : '+';
      item.querySelector('[id^="faq-panel-"]').hidden = !open;
    });

    document.querySelectorAll('#orders .vh-order').forEach(function (row, i) {
      var live = i === (state.tick % ORDERS.length);
      row.classList.toggle('is-live', live);
      row.querySelector('.vh-order__ago').textContent = live ? 'just now' : ORDERS[i][2];
    });
  }

  /* --- Wire up ------------------------------------------------------------- */

  buildPlans();
  buildScents();
  buildThumbs();
  buildMarquee();
  buildOrders();
  buildFaq();

  $('ship-window').textContent = shipWindow();

  function addToCart() { state.added = true; render(); }
  $('cta').addEventListener('click', addToCart);
  $('sticky-cta').addEventListener('click', addToCart);

  // One passive listener is enough in a real page; the prototype needed three
  // because it ran inside a scrolling host container.
  var sticky = $('sticky');
  function onScroll() { sticky.classList.toggle('is-visible', window.scrollY > 640); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  setInterval(function () { state.tick += 1; render(); }, 5200);

  /* Theme toggle — only present on the Cupertino skin, which reads
     data-ap-theme. With nothing set the design system follows the OS, so the
     button's job is to say what the click will do, not what the theme is. */
  var themeBtn = $('theme-toggle');
  if (themeBtn) {
    var root = document.documentElement;
    var isDark = function () {
      var set = root.getAttribute('data-ap-theme');
      return set ? set === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    };
    var label = function () { themeBtn.textContent = isDark() ? 'Light' : 'Dark'; };
    themeBtn.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      root.setAttribute('data-ap-theme', next);
      try { localStorage.setItem('vh-theme', next); } catch (e) {}
      label();
    });
    label();
  }

  render();
})();
