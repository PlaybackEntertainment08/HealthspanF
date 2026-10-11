# The Healthspan Standard 2027 — Website

Front-end for the Healthspan Standard 2027 summit (New Delhi, 10–11 April 2027),
organised by IASRM. Static HTML, CSS and vanilla JS, with the Bootstrap 5 grid
and GSAP/ScrollTrigger for motion.

The visual language is taken from the client's design mockup
(`Landing page-html/Main.dc.html`) and rebuilt as a proper design system; the
site architecture, page set and portal flows follow the reference site
`asvs2026.com`, upgraded.

---

## Running it

It is a static site — open `index.html`, or serve the folder:

```bash
python -m http.server 8080
# then http://localhost:8080
```

Serve it rather than opening from `file://`; Google Fonts and the CDN scripts
behave better over HTTP.

## Deploying

Upload the repository root as-is to any static host (Netlify, Vercel, GitHub
Pages, Hostinger, cPanel). There is no build step on the server.

Two things to set before go-live:

1. **Canonical domain.** `SITE` at the top of `_build/build.py` is
   `https://healthspanstandard.org/`. Change it to the real domain and re-run
   the build so canonicals, Open Graph URLs, JSON-LD and `sitemap.xml` all match.
2. **404 page.** Point the host's not-found handler at `/404.html`
   (`ErrorDocument 404 /404.html` on Apache, `error_page 404 /404.html` on nginx).

---

## How the pages are built

Every `.html` file in the root is **generated** — edit the sources, not the
output.

```
_build/
├── build.py              the generator; also writes sitemap.xml, robots.txt, site.webmanifest
├── check.py              link, anchor, JSON-LD, heading and label validation
├── make_images.py        regenerates the OG card and the PNG icons
├── retitle.py            one-off that set the SERP titles/descriptions
├── partials/base.html    the shell: head, topbar, header, nav, footer, scripts
└── pages/*.html          one file per page: JSON front-matter, a `---` line, then the body
```

```bash
python _build/build.py     # regenerate all 28 pages
python _build/check.py     # validate (exits non-zero on a problem)
python _build/make_images.py
```

The navigation lives in one place — the `NAV` list in `build.py`. Add an item
there and it appears on every page with the right `aria-current`.

### Page front-matter

```json
{
  "slug": "programme.html",
  "navKey": "programme",
  "title": "…", "description": "…",
  "crumbs": [["Programme", null], ["Scientific Programme", "programme.html"]],
  "pagehead": { "eyebrow": "…", "h1": "…", "lede": "…", "extra": "<optional html>" },
  "jsonld": [ { "@type": "FAQPage", "…": "…" } ],
  "robots": "noindex,nofollow",
  "priority": "0.9", "changefreq": "weekly"
}
```

`Organization`, `WebSite` and (where relevant) the `EducationEvent` graph are
added automatically, as is `BreadcrumbList` whenever `crumbs` is present.

---

## The pages

| | |
|---|---|
| `index.html` | Home — hero, countdown, preamble, programme tabs, rapid-fire, Longevity 40, passes, FAQ |
| `about.html` · `charter.html` · `books.html` | Why we gather · the Charter and house rule · the three book launches |
| `committee.html` · `faculty.html` · `venue.html` | Organising and scientific committees · faculty · venue and Delhi |
| `programme.html` · `rapid-fire.html` · `workshops.html` · `experience-lounge.html` | The scientific programme and its parallel streams |
| `abstracts.html` | Call for abstracts — nine categories, guidelines, submission form |
| `longevity-40.html` · `nominate.html` | The inaugural honours and the nomination form |
| `registration.html` · `login.html` · `payment.html` · `dashboard.html` | The delegate portal |
| `accommodation.html` · `visa.html` · `tour.html` · `downloads.html` · `faq.html` · `contact.html` | Delegate information |
| `sponsors.html` | Industry partners and sponsorship packages |
| `terms.html` · `privacy.html` · `404.html` | Legal and error |

---

## Connecting a backend

The portal screens are complete and fully interactive, but every call is
stubbed. There is exactly one function to replace:

```js
// assets/js/portal.js
HS.api = function (endpoint, payload) { … }   // ← point this at your API
```

Each form declares its own endpoint in markup, so nothing else needs touching:

```html
<form data-validate data-endpoint="/api/abstracts/create" data-success="…">
```

Endpoints currently declared:

| Endpoint | Where |
|---|---|
| `/api/auth/register`, `/api/auth/login`, `/api/auth/reset`, `/api/auth/change-password` | `login.html`, `dashboard.html` |
| `/api/registration/quote` | `registration.html` |
| `/api/payments/create-order` | `payment.html` |
| `/api/abstracts/create` | `abstracts.html`, `dashboard.html` |
| `/api/longevity40/nominate` | `nominate.html` |
| `/api/visa/request` | `dashboard.html` |
| `/api/profile/update`, `/api/invoices/update` | `dashboard.html` |
| `/api/sponsorship/enquire`, `/api/tours/interest`, `/api/contact` | `sponsors.html`, `tour.html`, `contact.html` |

### Fees

The whole rate card is one object, `HS.fees` in `portal.js` — passes, add-ons,
the three date-based tiers and the GST rate. `HS.quote()` builds a line-item
breakdown from it and drives both the registration configurator and the
checkout summary. The printed tables in `registration.html` must be kept in step
with it by hand.

**These figures are a preview only.** In production the server recomputes the
price and authorises the order; never trust the amount posted by the browser.

### Payment

`payment.html` collects the method and billing details and then hands off. It
never touches card data — create the order server-side and open the gateway
(Razorpay, PayU, CCAvenue, Stripe) with the order id returned. The handler to
replace is `HS.startPayment` in `portal.js`.

### Sessions

`HS.session` uses `sessionStorage` purely so the screens are demonstrable. Replace
it with an httpOnly, Secure, SameSite cookie set by the server.

---

## Design system

Everything is tokenised at the top of `assets/css/style.css`.

| | |
|---|---|
| Paper | `#F7F0E1` base, `#FFFDF7` raised, `#F4E8CB` band, `#EFE3C5` deep |
| Seal reds | `#4E120C` deep, `#6B1A12` maroon, `#8E2418` crimson |
| Gold leaf | `#D9AE52` gold, `#B8862B` dark, `#C9A56A` soft, `#D9C495` rule |
| Tricolour | `#E8872B` saffron, `#FFFFFF`, `#1E7A32` green |
| Evidence tiers | I `#8E2418` · II `#B8862B` · III `#C9A56A` · IV `#E2CC9A` |
| Type | Cinzel (display) · Cormorant Garamond (serif) · Jost (body) · Pinyon Script · Tiro Devanagari Sanskrit |

Type and spacing scale fluidly with `clamp()`, so there are no font-size
breakpoints to maintain.

## Motion

GSAP 3.12.5 with ScrollTrigger: a hero sequence, scroll reveals
(`data-reveal`, `data-reveal-group`), counters (`data-count`), parallax
(`data-parallax`), a tricolour scroll-progress bar and a CSS marquee.

Every animation is gated behind `prefers-reduced-motion: reduce`, and the
content is readable with JavaScript disabled — `.no-js` on `<html>` keeps the
reveal targets visible, the programme day panels both render, and the dashboard
shows every panel at once.

## Accessibility

WCAG 2.1 AA targeted: skip link, visible 3px focus rings, landmark elements,
one `<h1>` per page, labelled form controls with inline error messaging, ARIA
tab and accordion patterns with arrow-key support, 44px minimum touch targets,
`aria-live` form status, and full keyboard operation of the nav, tabs,
accordions and dashboard. `check.py` enforces the headings, labels and alt text.

## SEO

Unique title and meta description per page within SERP limits; canonicals;
Open Graph and Twitter cards; a JSON-LD graph (`Organization`, `WebSite`,
`EducationEvent` with `Offer` pricing, `BreadcrumbList`, `FAQPage`, `HowTo`,
`ItemList`, `Book`); semantic headings; descriptive alt text; a generated
`sitemap.xml` and `robots.txt`; `noindex` on `dashboard.html` and
`payment.html`; font preconnect and non-blocking font loading.

---

## Content still to come from the client

Placeholders are marked in the pages and dated where the client has given a date.

- Named patrons, organising team and scientific committee (Dec 2026)
- National and international faculty (Dec 2026 / Feb 2027)
- Confirmed venue name, address and floor plan (Dec 2026)
- Named partner hotels and nightly rates (Dec 2026)
- Sponsor logos as agreements are signed
- The PDFs referenced from `downloads.html` → drop into `assets/pdf/`
- Faculty and honouree photographs → `assets/img/`, then swap the initials
  placeholder inside `.person__portrait` for an `<img>`

Prices, dates and policies are modelled on the client's mockup and the reference
site's structure. **Have the secretariat confirm every figure in
`registration.html`, `terms.html` and `HS.fees` before go-live.**

---

© 2026–2027 IASRM. *Evidence before enthusiasm.*
