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
    refillDiscount: 0.15,   // email-only plan offer; nothing on this page reads it
    guaranteeDays: 30,
    warrantyDays: 90,
    reviewCount: 25089,
    showUrgency: true
  };

  /* Prices print without a trailing .00 — "$49", but "$59.90". */
  function money(n) { return '$' + n.toFixed(2).replace(/\.00$/, ''); }

  /* Dispatch date: same working day before the cut-off, otherwise the next one.
     This is the date the store controls, which is why it leads the delivery
     line — the arrival window below it is only an estimate. */
  function shipBy() {
    var d = new Date();
    if (d.getHours() >= 14) d = new Date(d.getTime() + 864e5);
    while (d.getDay() === 0 || d.getDay() === 6) d = new Date(d.getTime() + 864e5);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  /* Fulfilment estimate: today+5 to today+9. Replace with the real SLA. */
  function shipWindow() {
    var fmt = function (d) { return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); };
    var now = Date.now();
    return fmt(new Date(now + 5 * 864e5)) + '–' + fmt(new Date(now + 9 * 864e5));
  }

  var PLANS = [
    { title: 'Gun only', note: 'One unit, one pod included. Try it on the couch first.',
      price: OFFER.gunPrice, compare: 0, badge: '' },
    { title: 'Gun + 3 refill pods', note: 'About four months of weekly use. Cheapest way to get pods.',
      price: OFFER.bundlePrice, compare: OFFER.gunPrice + OFFER.refillPrice, badge: 'Most popular', badgeAccent: true }
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
    'Takes any water-based solution', OFFER.warrantyDays + '-day warranty', 'Refills ' + money(OFFER.refillPrice) + ' for three'
  ];

  var FAQS = [
    ['Does it actually remove pet odor, or just cover it?',
     'It neutralizes. The mist carries odor-binding agents into fabric instead of laying fragrance on top, which is why the smell does not come back the same evening. Deep, set-in odor on older upholstery may want a second pass.'],
    ['What smells does it handle?',
     'Wet dog, litter box, accidents on carpet, pet beds, couches, blankets, car seats, and the general background smell you have stopped noticing in your own home.'],
    ['Can I use my own solution?',
     'Yes, any water-based enzyme cleaner. Doing so will not void your warranty. What we will not do is promise a result we did not formulate. Our pods are pre-dosed for this atomiser, so those are the ones the ' + OFFER.guaranteeDays + '-day odor guarantee is written against. Use your own and the hardware is still covered; the outcome is yours.'],
    ['Is there anything I should not put in it?',
     'Water-based only. No gasoline, no oil-based products, no solvents, nothing thick or abrasive. The nozzle atomises to a very fine mist, and anything oily or heavy clogs it. Clog damage is the one thing the warranty does not cover.'],
    ['What if it breaks after three weeks?',
     'Then you send a photo of the serial plate and we ship a replacement from California. Nothing to mail back, no diagnostic call. The motor and battery are covered for ' + OFFER.warrantyDays + ' days, and the refund window runs the first ' + OFFER.guaranteeDays + ' regardless of why you want out.'],
    ['How do I get more pods?',
     'Three pods are ' + money(OFFER.refillPrice) + ', in whichever scent you want. Most households need them about every two months. We will email you before you run out, and you order in one click. Nothing is automatic and nothing is charged without you asking.'],
    ['Shipping and returns?',
     'Free US shipping over $50, dispatched from California, arriving ' + shipWindow() + ' with tracking. ' + OFFER.guaranteeDays + ' days for a full refund, and you keep the pods.']
  ];

  var state = { plan: 1, scent: 0, faq: 0, img: 0, added: false };

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
      btn.querySelector('.vh-plan__compare').textContent = p.compare ? money(p.compare) : '';
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

    $('plan-note').textContent = 'One-time purchase. Pods are '
      + money(OFFER.refillPrice) + ' for three whenever you need them.';

    var shot = GALLERY[state.img];
    $('hero-note').textContent = 'photo: ' + shot.short;
    var heroImg = $('hero-img');
    if (heroImg) {
      heroImg.onerror = function () { heroImg.style.display = 'none'; };
      heroImg.style.display = '';
      heroImg.src = shot.src;
    }

    var saving = plan.compare ? plan.compare - plan.price : 0;
    $('cta-label').textContent = state.added ? 'Added to cart'
      : (saving > 0 ? 'Add to cart — save ' + money(saving) : 'Add to cart');
    $('cta-price').textContent = state.added ? '✓' : money(plan.price);
    $('sticky-cta').textContent = state.added ? 'Added ✓' : 'Add — ' + money(plan.price);
    $('ship-by').textContent = shipBy();
    $('sticky-summary').textContent = summary;

    document.querySelectorAll('#faq-list .vh-faq__item').forEach(function (item, i) {
      var open = i === state.faq;
      item.querySelector('.vh-faq__q').setAttribute('aria-expanded', String(open));
      item.querySelector('.vh-faq__sign').textContent = open ? '–' : '+';
      item.querySelector('[id^="faq-panel-"]').hidden = !open;
    });

  }

  /* --- Wire up ------------------------------------------------------------- */

  buildPlans();
  buildScents();
  buildThumbs();
  buildMarquee();
  buildFaq();

  $('ship-window').textContent = shipWindow();
  $('ship-by').textContent = shipBy();

  function addToCart() { state.added = true; render(); }
  $('cta').addEventListener('click', addToCart);
  $('sticky-cta').addEventListener('click', addToCart);

  // One passive listener is enough in a real page; the prototype needed three
  // because it ran inside a scrolling host container.
  var sticky = $('sticky');
  function onScroll() { sticky.classList.toggle('is-visible', window.scrollY > 640); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();


  function isDarkNow() {
    var set = document.documentElement.getAttribute('data-ap-theme');
    return set ? set === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  /* Skin switch. The stylesheets are already in the document; switching is a
     matter of which pair is parked at media="not all". The label names the skin
     the click will move to, matching the theme button below. */
  var skinBtn = $('skin-toggle');
  if (skinBtn) {
    var root = document.documentElement;
    // A ?skin= override means this page is a pane in compare.html, so a click
    // here must not overwrite the reader's own saved preference.
    var pinned = new URLSearchParams(location.search).has('skin');
    var applySkin = function (skin) {
      var cupertino = skin === 'cupertino';
      $('skin-modernist-tokens').media = cupertino ? 'not all' : 'all';
      $('skin-modernist').media = cupertino ? 'not all' : 'all';
      $('skin-cupertino-tokens').media = cupertino ? 'all' : 'not all';
      $('skin-cupertino').media = cupertino ? 'all' : 'not all';
      root.setAttribute('data-vh-skin', skin);
      skinBtn.textContent = cupertino ? 'Modernist' : 'Cupertino';
    };
    skinBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-vh-skin') === 'cupertino' ? 'modernist' : 'cupertino';
      applySkin(next);
      if (!pinned) { try { localStorage.setItem('vh-skin', next); } catch (e) {} }
      if (themeBtn) themeBtn.textContent = isDarkNow() ? 'Light' : 'Dark';
    });
    applySkin(root.getAttribute('data-vh-skin') || 'modernist');
  }

  /* Theme toggle — only meaningful on the Cupertino skin, which reads
     data-ap-theme. With nothing set the design system follows the OS, so the
     button's job is to say what the click will do, not what the theme is. */
  var themeBtn = $('theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = isDarkNow() ? 'light' : 'dark';
      document.documentElement.setAttribute('data-ap-theme', next);
      try { localStorage.setItem('vh-theme', next); } catch (e) {}
      themeBtn.textContent = isDarkNow() ? 'Light' : 'Dark';
    });
    themeBtn.textContent = isDarkNow() ? 'Light' : 'Dark';
  }

  render();
})();
