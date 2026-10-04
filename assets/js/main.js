/* Blaha Residence – kis, függőségmentes JavaScript.
   Menü, görgetés-állapot, nyelvmegjegyzés, galéria-lightbox, űrlap. */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var pageLang = root.lang === 'en' ? 'en' : 'hu';
  var STORE_KEY = 'br-lang';

  function store(k, v) { try { if (v === undefined) { return localStorage.getItem(k); } localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- Nyelv megjegyzése ----------
     A magyar oldalról átirányít az angolra, ha a látogató korábban azt választotta.
     Csak a gyökér (HU) oldalon, és csak kifejezett nyelvváltás után tárolunk. */
  if (pageLang === 'hu' && store(STORE_KEY) === 'en') {
    var enLink = doc.querySelector('.lang-switch [data-lang="en"]');
    if (enLink) { location.replace(enLink.getAttribute('href') + location.hash); return; }
  }

  var header = doc.getElementById('site-header');
  var nav = doc.getElementById('main-nav');
  var toggle = doc.querySelector('.menu-toggle');
  var sections = [].slice.call(doc.querySelectorAll('main > section[id]'));
  var navLinks = [].slice.call(doc.querySelectorAll('.main-nav a[data-nav]'));
  var currentSection = 'home';

  /* ---------- Fejléc: átlátszó → tömör ---------- */
  function onScroll() {
    var solid = window.scrollY > 24;
    header.classList.toggle('is-solid', solid);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Mobilmenü ---------- */
  function setMenu(open) {
    nav.classList.toggle('is-open', open);
    header.classList.toggle('menu-open', open);
    doc.body.classList.toggle('no-scroll', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', toggle.getAttribute(open ? 'data-close' : 'data-open'));
  }
  var mq = window.matchMedia('(max-width: 1149px)');
  function syncNavA11y() {
    // zárt mobilmenüben a linkek ne legyenek fókuszálhatók
    if (mq.matches && !nav.classList.contains('is-open')) { nav.setAttribute('inert', ''); } else { nav.removeAttribute('inert'); }
  }
  syncNavA11y();
  mq.addEventListener('change', function () { setMenu(false); syncNavA11y(); });
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') !== 'true';
    setMenu(open); syncNavA11y();
    if (open) { var first = nav.querySelector('a'); if (first) first.focus({ preventScroll: true }); }
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) { setMenu(false); syncNavA11y(); }
  });
  doc.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) { setMenu(false); syncNavA11y(); toggle.focus(); }
  });

  /* ---------- Aktív menüpont + aktuális szekció (nyelvváltáshoz) ---------- */
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          var id = en.target.id;
          currentSection = id;
          navLinks.forEach(function (a) { a.classList.toggle('is-active', a.getAttribute('data-nav') === id); });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    sections.forEach(function (s) { spy.observe(s); });

    /* ---------- Görgetéses megjelenés ---------- */
    var reveals = [].slice.call(doc.querySelectorAll('.reveal'));
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    // enyhe lépcsőzés az egymás melletti elemeknél
    var groups = ['.cards', '.gallery', '.amenity-grid', '.rules-list'];
    groups.forEach(function (sel) {
      var parent = doc.querySelector(sel);
      if (!parent) return;
      [].slice.call(parent.children).forEach(function (c, i) { c.style.setProperty('--d', (i % 4) * 70 + 'ms'); });
    });
    reveals.forEach(function (r) { io.observe(r); });
  } else {
    [].forEach.call(doc.querySelectorAll('.reveal'), function (r) { r.classList.add('in'); });
  }

  /* ---------- Nyelvváltó: ugyanarra a szekcióra visz, és megjegyzi a választást ---------- */
  [].forEach.call(doc.querySelectorAll('.lang-switch a[data-lang]'), function (a) {
    a.addEventListener('click', function (e) {
      var target = a.getAttribute('data-lang');
      store(STORE_KEY, target);
      if (target === pageLang) { e.preventDefault(); return; }
      e.preventDefault();
      var hash = currentSection && currentSection !== 'home' ? '#' + currentSection : '';
      location.href = a.getAttribute('href') + hash;
    });
  });

  /* ---------- Galéria lightbox ---------- */
  var dlg = doc.getElementById('lightbox');
  var items = [].slice.call(doc.querySelectorAll('.g-btn'));
  var lbImg = doc.getElementById('lb-img');
  var lbCap = doc.getElementById('lb-cap');
  var lbCount = doc.getElementById('lb-count');
  var idx = 0, opener = null;

  function show(i) {
    idx = (i + items.length) % items.length;
    var b = items[idx];
    lbImg.classList.remove('x'); void lbImg.offsetWidth;
    lbImg.src = b.getAttribute('data-full');
    lbImg.alt = b.getAttribute('data-alt') || '';
    lbCap.textContent = b.getAttribute('data-cap') || '';
    lbCount.textContent = (idx + 1) + ' / ' + items.length;
    // szomszédos képek előtöltése
    [idx + 1, idx - 1].forEach(function (n) {
      var im = new Image(); im.src = items[(n + items.length) % items.length].getAttribute('data-full');
    });
  }
  function openLb(i, btn) {
    opener = btn;
    show(i);
    if (typeof dlg.showModal === 'function') { dlg.showModal(); } else { dlg.setAttribute('open', ''); }
    doc.body.classList.add('no-scroll');
  }
  function closeLb() {
    if (typeof dlg.close === 'function') { dlg.close(); } else { dlg.removeAttribute('open'); }
  }
  dlg.addEventListener('close', function () {
    doc.body.classList.remove('no-scroll');
    if (opener) { opener.focus({ preventScroll: true }); }
  });
  items.forEach(function (b, i) { b.addEventListener('click', function () { openLb(i, b); }); });
  dlg.addEventListener('click', function (e) {
    var act = e.target.closest('[data-lb]');
    if (act) {
      var a = act.getAttribute('data-lb');
      if (a === 'close') closeLb(); else if (a === 'prev') show(idx - 1); else show(idx + 1);
    } else if (!e.target.closest('#lb-img') && !e.target.closest('.lb-caption')) {
      closeLb(); // kattintás a háttérre
    }
  });
  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { show(idx - 1); } else if (e.key === 'ArrowRight') { show(idx + 1); }
  });
  // érintéses lapozás
  var tx = null;
  dlg.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
  dlg.addEventListener('touchend', function (e) {
    if (tx === null) return;
    var dx = e.changedTouches[0].clientX - tx; tx = null;
    if (Math.abs(dx) > 50) { show(idx + (dx < 0 ? 1 : -1)); }
  }, { passive: true });

  /* ---------- Kapcsolatfelvételi űrlap ---------- */
  var form = doc.getElementById('contact-form');
  if (!form) return;
  var T = {};
  try { T = JSON.parse(doc.getElementById('form-i18n').textContent); } catch (e) { /* üres szövegek */ }
  var status = doc.getElementById('form-status');
  var submitBtn = doc.getElementById('form-submit');
  var arrival = form.elements.arrival, departure = form.elements.departure;

  function iso(d) { var m = d.getMonth() + 1, day = d.getDate(); return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day; }
  var today = iso(new Date());
  arrival.min = today; departure.min = today;
  arrival.addEventListener('change', function () {
    if (arrival.value) {
      var d = new Date(arrival.value + 'T00:00:00'); d.setDate(d.getDate() + 1);
      departure.min = iso(d);
    }
  });

  function setErr(el, msg) {
    var box = doc.getElementById('err-' + el.name);
    if (!box) return;
    if (msg) { box.textContent = msg; box.hidden = false; el.setAttribute('aria-invalid', 'true'); }
    else { box.textContent = ''; box.hidden = true; el.removeAttribute('aria-invalid'); }
  }
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var phoneRe = /^\+?[0-9 ()\/.\-]{6,24}$/;

  function validateField(el) {
    var v = (el.type === 'checkbox') ? el.checked : el.value.trim();
    var msg = '';
    switch (el.name) {
      case 'name': if (!v) msg = T.required; break;
      case 'email': if (!v) msg = T.required; else if (!emailRe.test(v)) msg = T.email; break;
      case 'phone': if (v && !phoneRe.test(v)) msg = T.phone; break;
      case 'guests': if (!v) msg = T.guests; break;
      case 'arrival': if (!v) msg = T.required; else if (v < today) msg = T.arrivalPast; break;
      case 'departure': if (!v) msg = T.required; else if (arrival.value && v <= arrival.value) msg = T.departure; break;
      case 'consent': if (!v) msg = T.consent; break;
    }
    setErr(el, msg);
    return !msg;
  }
  var fields = ['name', 'email', 'phone', 'guests', 'arrival', 'departure', 'consent'].map(function (n) { return form.elements[n]; });
  fields.forEach(function (el) {
    el.addEventListener('blur', function () { if (el.value || el.checked || el.hasAttribute('aria-invalid')) validateField(el); });
    el.addEventListener('input', function () { if (el.hasAttribute('aria-invalid')) validateField(el); });
    el.addEventListener('change', function () { if (el.hasAttribute('aria-invalid')) validateField(el); });
  });
  arrival.addEventListener('change', function () { if (departure.value) validateField(departure); });

  function showStatus(kind, html) {
    status.className = 'form-status ' + (kind === 'success' ? 'is-success' : 'is-error');
    status.innerHTML = html;
    status.hidden = false;
    status.focus();
  }
  function phoneHtml() { return ' <a href="tel:' + T.phoneTel + '">' + T.phone + '</a>'; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    status.hidden = true;
    var firstBad = null;
    fields.forEach(function (el) { if (!validateField(el) && !firstBad) firstBad = el; });
    if (firstBad) { firstBad.focus(); showStatus('error', esc(T.summary)); return; }

    // Spam-csapda (robotok kitöltik): csendben nem küldünk semmit.
    if (form.elements.website.value) { return; }

    var payload = {
      lang: form.getAttribute('data-lang'),
      name: form.elements.name.value.trim(),
      email: form.elements.email.value.trim(),
      phone: form.elements.phone.value.trim(),
      arrival: arrival.value,
      departure: departure.value,
      guests: form.elements.guests.value,
      message: form.elements.message.value.trim()
    };

    /* ======================================================================
       ITT KÖTHETŐ BE AZ E-MAIL KÜLDÉS / EMAIL SENDING HOOK
       ----------------------------------------------------------------------
       A projektnek jelenleg nincs szerveroldali (backend) része, ezért az űrlap
       addig NEM küld el semmit, amíg meg nem adsz egy beküldési címet:
         - src/build.py  →  CONFIG["form_endpoint"]  (majd: python3 src/build.py)
         - pl. Formspree / Getform / saját API végpont: JSON POST-ot fogad,
           és 2xx válasszal jelzi a sikert.
       EmailJS-hez cseréld a lenti fetch-et az EmailJS küldő hívására
       (emailjs.send(...)), a sikeres/hibás ágak maradhatnak.
       ====================================================================== */
    var endpoint = form.getAttribute('data-endpoint');
    if (!endpoint) {
      if (window.console) console.warn('[Blaha Residence] Az űrlap nincs bekötve: állítsd be a CONFIG["form_endpoint"] értékét a src/build.py-ban.');
      showStatus('error', esc(T.notConfigured) + phoneHtml());
      return;
    }

    submitBtn.disabled = true; submitBtn.textContent = T.sending;
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      form.reset();
      form.closest('.form-card').classList.add('is-sent');
      showStatus('success', esc(T.success));
    }).catch(function () {
      showStatus('error', esc(T.failure) + phoneHtml());
    }).then(function () {
      submitBtn.disabled = false; submitBtn.textContent = T.submit;
    });
  });
})();
