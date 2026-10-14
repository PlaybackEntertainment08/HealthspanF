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
├── check.py              static validation: links, anchors, JSON-LD, headings, labels, alt text
├── qa.sh                 runtime QA in headless Chrome, per page per viewport
├── qa-harness.html       the page qa.sh injects to measure a live render
├── make_images.py        regenerates the OG card and the PNG icons
├── partials/base.html    the shell: head, topbar, header, nav, footer, scripts
└── pages/*.html          one file per page: JSON front-matter, a `---` line, then the body
```

```bash
python _build/build.py     # regenerate all 33 pages
python _build/check.py     # static validation (exits non-zero on a problem)
python _build/make_images.py
```

### Runtime QA

`check.py` reads the markup; it cannot see computed colour, layout or overflow.
`qa.sh` renders each page in headless Chrome at a given viewport and reports
horizontal overflow, elements outside the viewport, touch targets under 24px,
scroll-reveal targets still hidden while on screen, and WCAG AA contrast
failures measured from computed styles.

```bash
python -m http.server 8099          # in one terminal
bash _build/qa.sh 390 844           # all pages at iPhone width
bash _build/qa.sh 1440 900 index.html registration.html
```

The suite is clean on all 33 pages at 360, 390, 768, 1024, 1280, 1440 and
1920 CSS pixels. Run it after any CSS change — it catches the whole class of
bug that is invisible in the markup.

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

`__DAYS__` anywhere in a page or partial is replaced with the number of days
from the build date to 10 April 2027, so the countdown is real content before
any script runs. **Rebuild before deploying** or that figure goes stale.

---

## The pages

| | |
|---|---|
33 pages.

| | |
|---|---|
| `index.html` | Home — hero, countdown, preamble, programme tabs, rapid-fire, Longevity 40, passes, FAQ |
| `about.html` · `charter.html` · `books.html` | Why we gather · the Charter and house rule · the three book launches |
| `committee.html` · `organisers.html` · `collaborations.html` | Organising and scientific committees · IASRM · convening and affiliated bodies |
| `faculty.html` · `advisory-board.html` · `venue.html` | Faculty · international councillors by region · venue and Delhi |
| `programme.html` · `rapid-fire.html` · `workshops.html` · `allied-health.html` · `industry-workshop.html` · `experience-lounge.html` | The scientific programme and its parallel streams |
| `abstracts.html` | Call for abstracts — nine categories, guidelines, submission form |
| `longevity-40.html` · `nominate.html` | The inaugural honours and the nomination form |
| `registration.html` · `login.html` · `payment.html` · `dashboard.html` | The delegate portal |
| `accommodation.html` · `visa.html` · `tour.html` · `downloads.html` · `faq.html` · `contact.html` | Delegate information |
| `sponsors.html` | Industry partners and sponsorship packages |
| `terms.html` · `privacy.html` · `404.html` | Legal and error |

### Mapping to the reference site

Every page on `asvs2026.com` has an equivalent here:

| Reference | Here |
|---|---|
| `Organizing-committee.html` | `committee.html` |
| `Venous-Chapter-VSI.html` (parent society) | `organisers.html` |
| `ASVS-international-councilors.html` | `advisory-board.html` |
| `asian-venous-forum.html` (affiliated body) | `collaborations.html` |
| National / International Faculty (`Coming-soon.html`) | `faculty.html#national`, `#international` |
| `login.aspx` · `Registration.html` | `login.html` · `registration.html` · `payment.html` · `dashboard.html` |
| `abstract-category.html` | `abstracts.html` |
| `program.html` · `program.aspx` | `programme.html` · `dashboard.html#programme` |
| `ASVS_Allied_Health.pdf` | `allied-health.html` |
| Trainee programme PDF | `workshops.html` |
| `workshops.aspx` · `workshop.aspx` | `workshops.html` |
| `industry-workshop.html` | `industry-workshop.html` |
| `accomodation.html` · `visa.html` · `Tour.html` | `accommodation.html` · `visa.html` · `tour.html` |
| `our-sponsors.html` | `sponsors.html` |
| Brochure PDFs under Download | `downloads.html` |

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

### Surfaces, not descendant selectors

A dark surface re-points the ink tokens rather than restating colours for each
child:

```css
.hero,.pagehead,.section--maroon,.card--dark,.sitefooter,… {
  --ink:#F7F0E1; --ink-2:#F1E4C8; --crimson:#D9AE52; --rule:rgba(217,174,82,.34);
}
```

Anything nested inside reads correctly without a new rule, and a light
component dropped into a dark section (`.notice`, `.card`, `.table-wrap`,
inputs) restores the defaults the same way.

Two things deliberately opt out, because they must look identical on either
ground: **buttons**, which carry their own `--b-*` literals, and the
**topbar**, whose background is a literal. Anything that uses a remapped token
as a *background* rather than as ink has to do the same — that is the one trap
in this approach.

## Motion

- **Hero** — pure CSS keyframes, no JS. It is the most important content on
  the site, so it must not depend on a CDN script or on `requestAnimationFrame`.
  `animation-fill-mode: backwards` (never `both`) means that if animations
  never run, the content is simply visible.
- **Scroll reveals** — IntersectionObserver plus CSS transitions, with a
  positive bottom `rootMargin` so a section finishes animating before the
  reader reaches it. Compositor-driven, no per-element tween, and a 6-second
  failsafe reveals everything regardless.
- **GSAP 3.12.5 + ScrollTrigger** — counters (`data-count`) and parallax
  (`data-parallax`) only.
- **Scrolling** — one rAF-throttled loop drives the progress bar, the sticky
  header and the back-to-top button. Page height is cached and re-measured on
  resize; reading `scrollHeight` inside a scroll handler forces a synchronous
  reflow every frame and is the usual cause of sticky-feeling scroll.
- **Grain overlay** — a fixed layer with no `mix-blend-mode`. A blended
  full-viewport layer makes the compositor re-read the whole screen each frame.
- **The loader** — shown on the **first page of a session only**, never again
  while the visitor moves around. On a 28-plus-page static site a curtain on
  every click is just a wait, for content that is already there. It is off by
  default and opted into by the inline head script, so if the script,
  `sessionStorage` or CSS animations are unavailable the page simply shows.
  Because it only ever appears when that script ran, the same script can
  guarantee its removal; it also never takes pointer events.

Every animation is gated behind `prefers-reduced-motion: reduce`.

### Without JavaScript

`.no-js` on `<html>` is removed by an inline head script, before first paint —
not by `main.js`, which is deferred behind the GSAP CDN and would otherwise
leave the fallbacks showing for as long as that took, then reflow.

While `.no-js` applies, the site stays fully usable: the mobile nav renders as
a stacked list instead of an un-openable drawer, both programme days and both
auth panels render (they carry a literal `hidden` attribute), every accordion
is open, the dashboard shows all panels, the preloader is suppressed, and
nothing is hidden waiting to be revealed. The countdown is written into the
HTML at build time, so it reads as a real number rather than a placeholder
even before the script ticks it.

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
