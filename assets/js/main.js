/* ==========================================================================
   THE HEALTHSPAN STANDARD 2027 — Interaction & Motion
   Vanilla JS + GSAP/ScrollTrigger. Every animation is gated behind
   prefers-reduced-motion; every component degrades to usable static HTML.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var HAS_GSAP = typeof window.gsap !== 'undefined';
  var SUMMIT = new Date('2027-04-10T09:00:00+05:30').getTime();

  root.classList.remove('no-js');

  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };

  /* ----------------------------------------------------------------------
     Preloader — never traps the user; hard-released after 2.2s regardless.
     ---------------------------------------------------------------------- */
  function initPreloader() {
    var pre = $('.preloader');
    if (!pre) return;
    var release = function () { pre.classList.add('is-done'); };
    window.addEventListener('load', function () { setTimeout(release, REDUCED ? 0 : 420); });
    setTimeout(release, 2200);
  }

  /* ----------------------------------------------------------------------
     Header: stuck state, mobile drawer, dropdown menus (click + hover)
     ---------------------------------------------------------------------- */
  function initHeader() {
    var header = $('.siteheader');
    var toggle = $('.navtoggle');
    var nav = $('#primary-nav');
    var mq = window.matchMedia('(max-width: 960px)');

    if (header) {
      var onScroll = function () {
        header.classList.toggle('is-stuck', window.scrollY > 12);
      };
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }

    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!open));
        nav.classList.toggle('is-open', !open);
        doc.body.classList.toggle('nav-open', !open);
      });
    }

    $$('.nav__item--has-menu').forEach(function (item) {
      var btn = $('.nav__link', item);
      var menu = $('.nav__menu', item);
      if (!btn || !menu) return;

      var setOpen = function (open) {
        item.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', String(open));
        if (mq.matches) menu.style.height = open ? menu.scrollHeight + 'px' : '0px';
        else menu.style.height = '';
      };

      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var open = item.classList.contains('is-open');
        if (!mq.matches) {
          $$('.nav__item--has-menu.is-open').forEach(function (o) {
            if (o !== item) { o.classList.remove('is-open'); $('.nav__link', o).setAttribute('aria-expanded', 'false'); }
          });
        }
        setOpen(!open);
      });

      item.addEventListener('mouseenter', function () { if (!mq.matches) setOpen(true); });
      item.addEventListener('mouseleave', function () { if (!mq.matches) setOpen(false); });
      item.addEventListener('focusout', function (e) {
        if (!mq.matches && !item.contains(e.relatedTarget)) setOpen(false);
      });
    });

    doc.addEventListener('click', function (e) {
      if (mq.matches || e.target.closest('.nav__item--has-menu')) return;
      $$('.nav__item--has-menu.is-open').forEach(function (o) {
        o.classList.remove('is-open');
        $('.nav__link', o).setAttribute('aria-expanded', 'false');
      });
    });

    doc.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      $$('.nav__item--has-menu.is-open').forEach(function (o) {
        o.classList.remove('is-open');
        $('.nav__link', o).setAttribute('aria-expanded', 'false');
      });
      if (nav && nav.classList.contains('is-open') && toggle) {
        nav.classList.remove('is-open');
        doc.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });

    mq.addEventListener('change', function () {
      if (!mq.matches) {
        if (nav) nav.classList.remove('is-open');
        doc.body.classList.remove('nav-open');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        $$('.nav__menu').forEach(function (m) { m.style.height = ''; });
      }
    });
  }

  /* ----------------------------------------------------------------------
     Scroll progress bar + back to top
     ---------------------------------------------------------------------- */
  function initScrollUI() {
    var bar = $('.scroll-progress');
    var top = $('.backtotop');
    if (!bar && !top) return;
    var tick = function () {
      var max = doc.body.scrollHeight - window.innerHeight;
      var pct = max > 0 ? window.scrollY / max : 0;
      if (bar) bar.style.transform = 'scaleX(' + pct.toFixed(4) + ')';
      if (top) top.classList.toggle('is-visible', window.scrollY > 700);
    };
    tick();
    window.addEventListener('scroll', tick, { passive: true });
    if (top) {
      top.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: REDUCED ? 'auto' : 'smooth' });
      });
    }
  }

  /* ----------------------------------------------------------------------
     Countdown to 10 April 2027, 09:00 IST
     ---------------------------------------------------------------------- */
  function initCountdown() {
    var nodes = $$('[data-countdown]');
    var days = $$('[data-days-left]');
    if (!nodes.length && !days.length) return;

    var pad = function (n) { return n < 10 ? '0' + n : String(n); };

    var render = function () {
      var diff = Math.max(0, SUMMIT - Date.now());
      var d = Math.floor(diff / 864e5);
      var h = Math.floor(diff / 36e5) % 24;
      var m = Math.floor(diff / 6e4) % 60;
      var s = Math.floor(diff / 1e3) % 60;
      var map = { days: d, hours: pad(h), minutes: pad(m), seconds: pad(s) };
      nodes.forEach(function (n) {
        var k = n.getAttribute('data-countdown');
        if (map[k] !== undefined) n.textContent = map[k];
      });
      days.forEach(function (n) { n.textContent = d; });
    };

    render();
    setInterval(render, 1000);
  }

  /* ----------------------------------------------------------------------
     Tabs (programme days, auth, abstract categories)
     ---------------------------------------------------------------------- */
  function initTabs() {
    $$('[data-tabs]').forEach(function (group) {
      var tabs = $$('[role="tab"]', group);
      if (!tabs.length) return;

      var activate = function (tab, focus) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute('aria-selected', String(on));
          t.setAttribute('tabindex', on ? '0' : '-1');
          var panel = doc.getElementById(t.getAttribute('aria-controls'));
          if (panel) panel.hidden = !on;
          if (on && panel && HAS_GSAP && !REDUCED) {
            window.gsap.fromTo(panel, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5, ease: 'power2.out' });
          }
        });
        if (focus) tab.focus();
      };

      tabs.forEach(function (tab, i) {
        tab.addEventListener('click', function () { activate(tab); });
        tab.addEventListener('keydown', function (e) {
          var next = null;
          if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = tabs[(i + 1) % tabs.length];
          if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = tabs[(i - 1 + tabs.length) % tabs.length];
          if (e.key === 'Home') next = tabs[0];
          if (e.key === 'End') next = tabs[tabs.length - 1];
          if (next) { e.preventDefault(); activate(next, true); }
        });
      });
    });
  }

  /* ----------------------------------------------------------------------
     Accordion — animated height, honours reduced motion
     ---------------------------------------------------------------------- */
  function initAccordion() {
    $$('.accordion__btn').forEach(function (btn) {
      var panel = doc.getElementById(btn.getAttribute('aria-controls'));
      if (!panel) return;
      var single = btn.closest('[data-accordion="single"]');

      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') === 'true';

        if (single && !open) {
          $$('.accordion__btn[aria-expanded="true"]', single).forEach(function (other) {
            var op = doc.getElementById(other.getAttribute('aria-controls'));
            other.setAttribute('aria-expanded', 'false');
            if (op) op.style.height = '0px';
          });
        }

        btn.setAttribute('aria-expanded', String(!open));
        if (REDUCED) { panel.style.height = open ? '0px' : 'auto'; return; }
        if (open) {
          panel.style.height = panel.scrollHeight + 'px';
          requestAnimationFrame(function () { panel.style.height = '0px'; });
        } else {
          panel.style.height = panel.scrollHeight + 'px';
          panel.addEventListener('transitionend', function once() {
            if (btn.getAttribute('aria-expanded') === 'true') panel.style.height = 'auto';
            panel.removeEventListener('transitionend', once);
          });
        }
      });
    });
  }

  /* ----------------------------------------------------------------------
     Copy-to-clipboard (bank details, emails)
     ---------------------------------------------------------------------- */
  function initCopy() {
    $$('[data-copy]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var text = btn.getAttribute('data-copy');
        var done = function () {
          var old = btn.textContent;
          btn.textContent = 'Copied';
          setTimeout(function () { btn.textContent = old; }, 1600);
        };
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
        else done();
      });
    });
  }

  /* ----------------------------------------------------------------------
     Motion: reveals, counters, parallax, hero sequence
     ---------------------------------------------------------------------- */
  function initMotion() {
    if (!HAS_GSAP || REDUCED) {
      root.classList.add('reveal-ready');
      $$('[data-count]').forEach(function (n) { n.textContent = n.getAttribute('data-count'); });
      return;
    }

    var gsap = window.gsap;
    if (window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);

    /* Hero entrance */
    var hero = $('[data-hero]');
    if (hero) {
      var seq = gsap.timeline({ defaults: { ease: 'power3.out', clearProps: 'transform' }, delay: .55 });
      seq.from('[data-hero-item]', { y: 26, opacity: 0, duration: .85, stagger: .085 });
      var emblem = $('.hero__emblem');
      if (emblem) seq.from(emblem, { scale: .86, rotate: -14, opacity: 0, duration: 1.1, ease: 'back.out(1.5)' }, .15);
      var sky = $('.hero__skyline');
      if (sky) seq.from(sky, { y: 40, opacity: 0, duration: 1.2 }, '-=.6');
    }

    /* Section reveals.
       GSAP's `from` renders the start state immediately, so the element is
       held hidden until its trigger — do not gsap.set() it visible here. */
    $$('[data-reveal]').forEach(function (el) {
      var mode = el.getAttribute('data-reveal') || 'up';
      var from = { opacity: 0, duration: .9, ease: 'power3.out' };
      if (mode === 'up') from.y = 34;
      if (mode === 'left') from.x = -36;
      if (mode === 'right') from.x = 36;
      if (mode === 'scale') { from.scale = .95; from.y = 20; }
      from.scrollTrigger = { trigger: el, start: 'top 88%', once: true };
      from.clearProps = 'opacity,transform';
      gsap.from(el, from);
    });

    /* Staggered children */
    $$('[data-reveal-group]').forEach(function (group) {
      var kids = Array.prototype.slice.call(group.children);
      gsap.from(kids, {
        y: 30, opacity: 0, duration: .8, ease: 'power3.out', stagger: .085,
        clearProps: 'opacity,transform',
        scrollTrigger: { trigger: group, start: 'top 88%', once: true }
      });
    });

    /* Counters */
    $$('[data-count]').forEach(function (el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var suffix = el.getAttribute('data-count-suffix') || '';
      var obj = { v: 0 };
      gsap.to(obj, {
        v: target, duration: 1.8, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true },
        onUpdate: function () { el.textContent = Math.round(obj.v) + suffix; }
      });
    });

    /* Parallax */
    $$('[data-parallax]').forEach(function (el) {
      var amt = parseFloat(el.getAttribute('data-parallax')) || 40;
      gsap.to(el, {
        yPercent: amt, ease: 'none',
        scrollTrigger: { trigger: el.parentElement || el, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });

    /* Draw the agenda spine as the day scrolls past */
    $$('[data-draw-line]').forEach(function (el) {
      gsap.fromTo(el, { scaleY: 0 }, {
        scaleY: 1, transformOrigin: '50% 0%', ease: 'none',
        scrollTrigger: { trigger: el.parentElement, start: 'top 70%', end: 'bottom 70%', scrub: .5 }
      });
    });

    root.classList.add('reveal-ready');
  }

  /* ----------------------------------------------------------------------
     Smooth in-page anchors with sticky-header offset
     ---------------------------------------------------------------------- */
  function initAnchors() {
    doc.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href');
      if (!id || id === '#' || id.length < 2) return;
      var target = doc.getElementById(id.slice(1));
      if (!target) return;
      e.preventDefault();
      var nav = $('.siteheader');
      var offset = (nav ? nav.offsetHeight : 0) + 18;
      var y = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: y, behavior: REDUCED ? 'auto' : 'smooth' });
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      var drawer = $('#primary-nav');
      var toggle = $('.navtoggle');
      if (drawer && drawer.classList.contains('is-open')) {
        drawer.classList.remove('is-open');
        doc.body.classList.remove('nav-open');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ----------------------------------------------------------------------
     Boot
     ---------------------------------------------------------------------- */
  function boot() {
    initPreloader();
    initHeader();
    initScrollUI();
    initCountdown();
    initTabs();
    initAccordion();
    initCopy();
    initAnchors();
    initMotion();
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
