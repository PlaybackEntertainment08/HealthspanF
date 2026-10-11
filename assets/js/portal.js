/* ==========================================================================
   THE HEALTHSPAN STANDARD 2027 — Delegate Portal
   --------------------------------------------------------------------------
   Front-end only. Validation, the fee engine, the registration configurator,
   the dashboard and the payment hand-off are all implemented here so the
   screens are fully demonstrable. Every place that must talk to a server is
   marked // >>> BACKEND and funnels through HS.api() — swap that one function
   for real endpoints and the UI needs no further change.

   NOTE ON SECURITY: prices are recomputed and authorised server-side in
   production. The client-side figures below drive the preview only.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };

  var HS = window.HS = window.HS || {};

  /* ======================================================================
     FEE SCHEDULE — single source of truth for every price on the site
     ====================================================================== */
  var TIERS = [
    { id: 'early',    label: 'Early rate',    until: '2026-12-31T23:59:59+05:30' },
    { id: 'standard', label: 'Standard rate', until: '2027-03-15T23:59:59+05:30' },
    { id: 'late',     label: 'Late & on-site rate', until: '2027-04-11T23:59:59+05:30' }
  ];

  var PASSES = {
    delegate:    { name: 'Two-Day Delegate Pass', heads: 1, inr: [51000, 59000, 68000],   usd: [555, 645, 745] },
    couple:      { name: 'Couple Pass',           heads: 2, inr: [90000, 104000, 120000], usd: [1000, 1150, 1325] },
    group:       { name: 'Group Pass (five)',     heads: 5, inr: [190000, 225000, 260000],usd: [2100, 2475, 2860] },
    residential: { name: 'Residential Pass',      heads: 1, inr: [100000, 115000, 132000],usd: [1100, 1265, 1450] },
    pg:          { name: 'PG Student / Trainee',  heads: 1, inr: [28000, 34000, 40000],   usd: [310, 375, 440] },
    allied:      { name: 'Allied Health & Nursing', heads: 1, inr: [22000, 26000, 31000], usd: [245, 290, 345] },
    accompanying:{ name: 'Accompanying Person',   heads: 1, inr: [18000, 21000, 25000],   usd: [200, 235, 275] }
  };

  var ADDONS = {
    workshop: { name: 'Pre-Summit Regenerative Skills Workshop (9 April)', inr: 9000, usd: 110 },
    gala:     { name: 'Additional Gala Dinner seat (10 April)',            inr: 6500, usd: 75 },
    lounge:   { name: 'Full Experience Lounge biomarker panel',            inr: 7500, usd: 90 }
  };

  var GST_RATE = 0.18;

  HS.fees = { TIERS: TIERS, PASSES: PASSES, ADDONS: ADDONS, GST_RATE: GST_RATE };

  HS.currentTier = function (now) {
    var t = (now || new Date()).getTime();
    for (var i = 0; i < TIERS.length; i++) {
      if (t <= new Date(TIERS[i].until).getTime()) return i;
    }
    return TIERS.length - 1;
  };

  HS.money = function (amount, currency) {
    try {
      return new Intl.NumberFormat(currency === 'INR' ? 'en-IN' : 'en-US', {
        style: 'currency', currency: currency, maximumFractionDigits: 0
      }).format(amount);
    } catch (e) {
      return (currency === 'INR' ? '₹' : '$') + amount.toLocaleString();
    }
  };

  /* Quote builder — pass id + add-ons + residency → full line-item breakdown */
  HS.quote = function (opts) {
    var tier = typeof opts.tier === 'number' ? opts.tier : HS.currentTier();
    var currency = opts.currency === 'USD' ? 'USD' : 'INR';
    var key = currency === 'USD' ? 'usd' : 'inr';
    var pass = PASSES[opts.pass] || PASSES.delegate;
    var lines = [{ label: pass.name + ' · ' + TIERS[tier].label, amount: pass[key][tier] }];

    (opts.addons || []).forEach(function (a) {
      if (ADDONS[a]) lines.push({ label: ADDONS[a].name, amount: ADDONS[a][key] });
    });

    var subtotal = lines.reduce(function (s, l) { return s + l.amount; }, 0);
    /* GST applies to Indian-rupee invoices; USD invoices are billed as export of service. */
    var gst = currency === 'INR' ? Math.round(subtotal * GST_RATE) : 0;

    return {
      currency: currency, tier: tier, tierLabel: TIERS[tier].label,
      lines: lines, subtotal: subtotal, gst: gst, total: subtotal + gst,
      heads: pass.heads, passName: pass.name
    };
  };

  /* ======================================================================
     API SHIM  // >>> BACKEND
     Replace the body of HS.api with real fetch() calls. Shape is kept
     deliberately boring: { ok, data, message }.
     ====================================================================== */
  HS.api = function (endpoint, payload) {
    return new Promise(function (resolve) {
      setTimeout(function () {
        console.info('[HS.api] ' + endpoint, payload);
        resolve({ ok: true, data: payload, message: 'Simulated response — connect a backend at ' + endpoint });
      }, 700);
    });
  };

  /* ======================================================================
     SESSION — demo only; a real build uses an httpOnly session cookie.
     ====================================================================== */
  HS.session = {
    read: function () {
      try { return JSON.parse(sessionStorage.getItem('hs.delegate') || 'null'); }
      catch (e) { return null; }
    },
    write: function (d) {
      try { sessionStorage.setItem('hs.delegate', JSON.stringify(d)); } catch (e) {}
    },
    clear: function () { try { sessionStorage.removeItem('hs.delegate'); } catch (e) {} }
  };

  /* ======================================================================
     VALIDATION
     ====================================================================== */
  var RULES = {
    email: { test: function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }, msg: 'Enter a valid email address.' },
    tel:   { test: function (v) { return /^[+]?[\d\s()-]{8,18}$/.test(v); }, msg: 'Enter a valid phone number, with country code.' },
    name:  { test: function (v) { return v.trim().length >= 2; }, msg: 'Please enter at least two characters.' },
    pwd:   { test: function (v) { return v.length >= 8 && /[a-zA-Z]/.test(v) && /\d/.test(v); }, msg: 'At least 8 characters, with a letter and a number.' }
  };

  function setFieldError(input, message) {
    var field = input.closest('.field') || input.closest('.check');
    if (!field) return;
    field.classList.toggle('is-invalid', !!message);
    input.setAttribute('aria-invalid', message ? 'true' : 'false');
    var slot = $('.field__error', field);
    if (slot) slot.textContent = message || '';
  }

  function validateInput(input) {
    var value = input.value || '';
    var required = input.hasAttribute('required');

    if (input.type === 'checkbox') {
      var bad = required && !input.checked;
      setFieldError(input, bad ? (input.getAttribute('data-msg') || 'This confirmation is required.') : '');
      return !bad;
    }
    if (required && !value.trim()) {
      setFieldError(input, input.getAttribute('data-msg') || 'This field is required.');
      return false;
    }
    if (!value.trim()) { setFieldError(input, ''); return true; }

    var rule = RULES[input.getAttribute('data-rule')];
    if (rule && !rule.test(value)) { setFieldError(input, rule.msg); return false; }

    var match = input.getAttribute('data-match');
    if (match) {
      var other = doc.getElementById(match);
      if (other && other.value !== value) { setFieldError(input, 'The two entries do not match.'); return false; }
    }
    setFieldError(input, '');
    return true;
  }

  function initValidation() {
    $$('form[data-validate]').forEach(function (form) {
      var controls = $$('input, select, textarea', form);

      controls.forEach(function (input) {
        input.addEventListener('blur', function () { validateInput(input); });
        input.addEventListener('input', function () {
          if ((input.closest('.field') || {}).classList && input.closest('.field').classList.contains('is-invalid')) validateInput(input);
        });
      });

      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var firstBad = null;
        controls.forEach(function (input) {
          if (!validateInput(input) && !firstBad) firstBad = input;
        });

        var status = $('[data-form-status]', form);
        if (firstBad) {
          if (status) {
            status.hidden = false;
            status.className = 'notice notice--alert';
            status.innerHTML = '<div><strong class="notice__title">Please check the form</strong>Some entries need attention before this can be submitted.</div>';
          }
          firstBad.focus();
          return;
        }

        var btn = $('[type="submit"]', form);
        var label = btn ? btn.textContent : '';
        if (btn) { btn.setAttribute('aria-disabled', 'true'); btn.textContent = 'Please wait…'; }

        var data = {};
        new FormData(form).forEach(function (v, k) {
          if (data[k] === undefined) data[k] = v;
          else if (Array.isArray(data[k])) data[k].push(v);
          else data[k] = [data[k], v];
        });

        // >>> BACKEND — point this endpoint at your API
        HS.api(form.getAttribute('data-endpoint') || '/api/submit', data).then(function (res) {
          if (btn) { btn.removeAttribute('aria-disabled'); btn.textContent = label; }
          var onDone = form.getAttribute('data-on-success');
          if (onDone && typeof HS[onDone] === 'function') { HS[onDone](data, res, form); return; }
          if (status) {
            status.hidden = false;
            status.className = 'notice notice--ok';
            status.innerHTML = '<div><strong class="notice__title">Received</strong>' +
              (form.getAttribute('data-success') || 'Thank you — the secretariat will be in touch by email.') + '</div>';
          }
          form.reset();
        });
      });
    });
  }

  /* ======================================================================
     AUTH — sign in / sign up / reset
     ====================================================================== */
  HS.afterSignIn = function (data) {
    HS.session.write({ email: data.email, name: data.email.split('@')[0], ref: 'HS27-' + Math.floor(100000 + Math.random() * 899999) });
    window.location.href = 'dashboard.html';
  };

  HS.afterSignUp = function (data) {
    HS.session.write({ email: data.email, name: [data.firstName, data.lastName].filter(Boolean).join(' '), ref: 'HS27-' + Math.floor(100000 + Math.random() * 899999) });
    window.location.href = 'registration.html#configure';
  };

  function initAuthExtras() {
    $$('[data-toggle-password]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var input = doc.getElementById(btn.getAttribute('data-toggle-password'));
        if (!input) return;
        var show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        btn.textContent = show ? 'Hide' : 'Show';
        btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
      });
    });
  }

  /* ======================================================================
     REGISTRATION CONFIGURATOR — live quote
     ====================================================================== */
  function initConfigurator() {
    var form = $('[data-configurator]');
    if (!form) return;

    var out = {
      lines: $('[data-quote-lines]'),
      sub: $('[data-quote-subtotal]'),
      gstRow: $('[data-quote-gst-row]'),
      gst: $('[data-quote-gst]'),
      total: $('[data-quote-total]'),
      tier: $('[data-quote-tier]'),
      heads: $('[data-quote-heads]')
    };

    function recalc() {
      var currency = (form.querySelector('[name="currency"]:checked') || {}).value || 'INR';
      var pass = (form.querySelector('[name="pass"]:checked') || {}).value || 'delegate';
      var addons = $$('[name="addon"]:checked', form).map(function (i) { return i.value; });
      var q = HS.quote({ pass: pass, addons: addons, currency: currency });

      if (out.lines) {
        out.lines.innerHTML = q.lines.map(function (l) {
          return '<div class="summary__row"><span>' + l.label + '</span><span class="tabular">' + HS.money(l.amount, q.currency) + '</span></div>';
        }).join('');
      }
      if (out.sub) out.sub.textContent = HS.money(q.subtotal, q.currency);
      if (out.gstRow) out.gstRow.hidden = q.gst === 0;
      if (out.gst) out.gst.textContent = HS.money(q.gst, q.currency);
      if (out.total) out.total.textContent = HS.money(q.total, q.currency);
      if (out.tier) out.tier.textContent = q.tierLabel;
      if (out.heads) out.heads.textContent = q.heads + (q.heads === 1 ? ' delegate' : ' delegates');

      /* PG proof upload appears only for the student rate */
      var proof = $('[data-pg-proof]');
      if (proof) {
        proof.hidden = pass !== 'pg';
        $$('input', proof).forEach(function (i) { if (pass !== 'pg') i.removeAttribute('required'); else i.setAttribute('required', ''); });
      }
      /* Residential pass reveals the hotel + nights picker */
      var stay = $('[data-stay-options]');
      if (stay) stay.hidden = pass !== 'residential';

      try { sessionStorage.setItem('hs.quote', JSON.stringify({ pass: pass, addons: addons, currency: currency })); } catch (e) {}
    }

    form.addEventListener('change', recalc);
    recalc();
  }

  /* Render the saved quote on the payment screen */
  function initCheckout() {
    var box = $('[data-checkout-summary]');
    if (!box) return;
    var saved = {};
    try { saved = JSON.parse(sessionStorage.getItem('hs.quote') || '{}'); } catch (e) {}
    var q = HS.quote({ pass: saved.pass, addons: saved.addons, currency: saved.currency });

    var html = q.lines.map(function (l) {
      return '<div class="summary__row"><span>' + l.label + '</span><span class="tabular">' + HS.money(l.amount, q.currency) + '</span></div>';
    }).join('');
    html += '<div class="summary__row"><span>Subtotal</span><span class="tabular">' + HS.money(q.subtotal, q.currency) + '</span></div>';
    if (q.gst) html += '<div class="summary__row"><span>GST @ 18%</span><span class="tabular">' + HS.money(q.gst, q.currency) + '</span></div>';
    html += '<div class="summary__row summary__row--total"><span>Amount due</span><span class="tabular">' + HS.money(q.total, q.currency) + '</span></div>';
    box.innerHTML = html;

    $$('[data-checkout-total]').forEach(function (n) { n.textContent = HS.money(q.total, q.currency); });

    /* Bank-transfer panel shows only when that method is chosen */
    $$('[name="paymethod"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        var bank = $('[data-bank-panel]');
        if (bank) bank.hidden = radio.value !== 'neft' || !radio.checked;
        var cta = $('[data-pay-cta]');
        if (cta) cta.textContent = radio.value === 'neft' ? 'Confirm and email me the invoice' : 'Pay securely now';
      });
    });
  }

  /* The configurator's submit: persist the quote, then go to checkout. */
  HS.afterQuote = function (data) {
    try {
      sessionStorage.setItem('hs.quote', JSON.stringify({
        pass: data.pass, addons: [].concat(data.addon || []), currency: data.currency
      }));
      sessionStorage.setItem('hs.delegateDraft', JSON.stringify({
        name: [data.firstName, data.lastName].filter(Boolean).join(' '), email: data.email
      }));
    } catch (e) {}
    window.location.href = 'payment.html';
  };

  /* >>> BACKEND — gateway hand-off.
     Create the order server-side, then open the gateway with the order id. */
  HS.startPayment = function (data, res, form) {
    var status = $('[data-form-status]', form);
    var method = data.paymethod || 'card';
    if (status) {
      status.hidden = false;
      status.className = 'notice';
      status.innerHTML = method === 'neft'
        ? '<div><strong class="notice__title">Proforma invoice on its way</strong>We have emailed a proforma invoice with the account details. Send the UTR number to accounts@healthspanstandard.org once the transfer is made.</div>'
        : '<div><strong class="notice__title">Opening the secure gateway…</strong>In the live build this hands off to the payment gateway with a server-created order id. You are never asked for card details on this page.</div>';
      status.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  /* ======================================================================
     DASHBOARD
     ====================================================================== */
  function initDashboard() {
    var dash = $('[data-dashboard]');
    if (!dash) return;
    dash.classList.add('is-enhanced');

    var who = HS.session.read();
    $$('[data-delegate-name]').forEach(function (n) { if (who && who.name) n.textContent = who.name; });
    $$('[data-delegate-ref]').forEach(function (n) { if (who && who.ref) n.textContent = who.ref; });
    $$('[data-delegate-email]').forEach(function (n) { if (who && who.email) n.textContent = who.email; });

    var links = $$('.dashnav a', dash);
    function show(hash) {
      var id = (hash || '').replace('#', '') || 'overview';
      var found = false;
      $$('.dashpanel', dash).forEach(function (p) {
        var on = p.id === id;
        p.classList.toggle('is-active', on);
        if (on) found = true;
      });
      if (!found) { var first = $('.dashpanel', dash); if (first) first.classList.add('is-active'); }
      links.forEach(function (a) {
        var on = a.getAttribute('href') === '#' + id;
        a.classList.toggle('is-active', on);
        if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
      });
    }

    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var h = a.getAttribute('href');
        history.replaceState(null, '', h);
        show(h);
      });
    });

    var logout = $('[data-logout]');
    if (logout) {
      logout.addEventListener('click', function (e) {
        e.preventDefault();
        HS.session.clear();
        window.location.href = 'login.html';
      });
    }

    show(window.location.hash);
  }

  /* ====================================================================== */
  function boot() {
    initValidation();
    initAuthExtras();
    initConfigurator();
    initCheckout();
    initDashboard();
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
