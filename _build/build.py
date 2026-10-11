#!/usr/bin/env python3
"""
Static site generator — The Healthspan Standard 2027.

Every page in the site root is produced from:
  _build/partials/base.html   the shell (head, header, nav, footer, scripts)
  _build/pages/<slug>.html    JSON front-matter, a line of '---', then the body

Run:  python _build/build.py
It also writes sitemap.xml, robots.txt and site.webmanifest.
"""

import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = os.path.join(HERE, "pages")
PARTIALS = os.path.join(HERE, "partials")

SITE = "https://healthspanstandard.org/"
TODAY = date.today().isoformat()
DAYS_TO_SUMMIT = max(0, (date(2027, 4, 10) - date.today()).days)

# ---------------------------------------------------------------------------
# Navigation — one definition, rendered into every page
# ---------------------------------------------------------------------------
NAV = [
    {"label": "Home", "href": "index.html", "key": "home"},
    {"label": "The Summit", "key": "summit", "children": [
        ("Why We Gather", "about.html", "The case for a healthspan standard"),
        ("The Charter", "charter.html", "Read, argued, amended, signed"),
        ("The House Rule", "charter.html#house-rule", "Evidence tiers on every slide"),
        ("Three Books", "books.html", "Unveiled from the stage"),
        ("Organising Committee", "committee.html", "Patrons, chairs and secretariat"),
        ("Venue &amp; Delhi", "venue.html", "Getting there, staying, seeing the city"),
    ]},
    {"label": "Programme", "key": "programme", "children": [
        ("Scientific Programme", "programme.html", "Eleven sessions across two days"),
        ("Rapid-Fire Rounds", "rapid-fire.html", "Thirty talks of six minutes"),
        ("Workshops &amp; Masterclasses", "workshops.html", "Hands-on, 9 April"),
        ("The Experience Lounge", "experience-lounge.html", "Try the tests you order"),
        ("Abstracts &amp; Submissions", "abstracts.html", "Categories, rules, deadlines"),
    ]},
    {"label": "Faculty", "key": "faculty", "children": [
        ("National Faculty", "faculty.html#national", "From across India"),
        ("International Faculty", "faculty.html#international", "Invited from abroad"),
        ("Scientific Committee", "committee.html#scientific", "Who reviews the programme"),
    ]},
    {"label": "Longevity 40", "key": "l40", "children": [
        ("The Inaugural Honours", "longevity-40.html", "Forty names, independently chosen"),
        ("The Categories", "longevity-40.html#categories", "Eleven fields of work"),
        ("Nominate a Colleague", "nominate.html", "Open until 31 January 2027"),
    ]},
    {"label": "Delegates", "key": "delegates", "children": [
        ("Registration &amp; Fees", "registration.html", "Passes, inclusions, rates"),
        ("Accommodation", "accommodation.html", "Partner hotels in Aerocity"),
        ("Visa &amp; Travel", "visa.html", "e-Business visa and invitation letters"),
        ("Delhi Tours", "tour.html", "Day tours and the Agra extension"),
        ("Downloads", "downloads.html", "Brochures and the programme PDF"),
        ("Frequently Asked Questions", "faq.html", "Answers for delegates"),
        ("Contact the Secretariat", "contact.html", "Who to write to"),
    ]},
    {"label": "Partners", "key": "partners", "children": [
        ("Industry Partners", "sponsors.html", "Who stands behind the summit"),
        ("Sponsorship Packages", "sponsors.html#packages", "Tiers and what they include"),
    ]},
]


def render_nav(active_key, slug):
    out = []
    for i, item in enumerate(NAV):
        kids = item.get("children")
        current = item.get("key") == active_key
        if not kids:
            aria = ' aria-current="page"' if slug == item["href"] else ""
            out.append(
                '      <div class="nav__item">'
                f'<a class="nav__link" href="{item["href"]}"{aria}>{item["label"]}</a></div>'
            )
            continue

        menu_id = f"navmenu-{i}"
        links = []
        for label, href, note in kids:
            aria = ' aria-current="page"' if href == slug else ""
            links.append(
                f'          <li><a href="{href}"{aria}>{label}'
                f'<span class="nav__note">{note}</span></a></li>'
            )
        cur_attr = ' aria-current="true"' if current else ""
        out.append(
            '      <div class="nav__item nav__item--has-menu">\n'
            '        <button class="nav__link" type="button" aria-expanded="false" '
            f'aria-controls="{menu_id}"{cur_attr}>'
            f'{item["label"]}<span class="nav__caret" aria-hidden="true"></span></button>\n'
            f'        <ul class="nav__menu" id="{menu_id}">\n'
            + "\n".join(links)
            + "\n        </ul>\n      </div>"
        )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Structured data
# ---------------------------------------------------------------------------
ORGANISATION = {
    "@type": "Organization",
    "@id": SITE + "#organisation",
    "name": "International Association of Stemcell & Regenerative Medicine",
    "alternateName": "IASRM",
    "url": "https://www.iasrmglobal.org",
    "email": "info@iasrmglobal.org",
    "telephone": "+91-98104-18415",
    "logo": SITE + "assets/img/favicon.svg",
    "sameAs": [
        "https://www.linkedin.com/company/iasrm",
        "https://x.com/iasrmglobal",
        "https://www.instagram.com/iasrmglobal",
        "https://www.youtube.com/@iasrm",
    ],
}

WEBSITE = {
    "@type": "WebSite",
    "@id": SITE + "#website",
    "url": SITE,
    "name": "Healthspan Standard 2027",
    "inLanguage": "en-IN",
    "publisher": {"@id": SITE + "#organisation"},
}

EVENT = {
    "@type": "MedicalBusinessEvent" if False else "EducationEvent",
    "@id": SITE + "#event",
    "name": "The Healthspan Standard 2027",
    "alternateName": "Healthspan Standard Summit — Delhi 2027",
    "description": (
        "Two days on evidence in longevity and regenerative medicine: thirty-six lectures, "
        "thirty rapid-fire talks, three panels, three book launches, the inaugural Longevity 40 "
        "honours, and a Charter read, argued and signed in Delhi."
    ),
    "startDate": "2027-04-10T07:00:00+05:30",
    "endDate": "2027-04-11T16:30:00+05:30",
    "eventStatus": "https://schema.org/EventScheduled",
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "inLanguage": "en",
    "image": [SITE + "assets/img/og-healthspan-standard-2027.png"],
    "url": SITE,
    "location": {
        "@type": "Place",
        "name": "New Delhi, India",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "New Delhi",
            "addressRegion": "Delhi",
            "addressCountry": "IN",
        },
    },
    "organizer": {"@id": SITE + "#organisation"},
    "performer": {"@id": SITE + "#organisation"},
    "audience": {"@type": "MedicalAudience", "audienceType": "Healthcare professionals"},
    "isAccessibleForFree": False,
    "maximumAttendeeCapacity": 1200,
    "offers": [
        {
            "@type": "Offer",
            "name": "Two-Day Delegate Pass — early rate",
            "price": "51000",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock",
            "validFrom": "2026-10-01T00:00:00+05:30",
            "validThrough": "2026-12-31T23:59:59+05:30",
            "url": SITE + "registration.html",
        },
        {
            "@type": "Offer",
            "name": "Two-Day Delegate Pass — standard rate",
            "price": "59000",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock",
            "validFrom": "2027-01-01T00:00:00+05:30",
            "validThrough": "2027-03-15T23:59:59+05:30",
            "url": SITE + "registration.html",
        },
    ],
}


def breadcrumbs(crumbs, slug):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE}]
    for i, (name, href) in enumerate(crumbs, start=2):
        entry = {"@type": "ListItem", "position": i, "name": name}
        if href:
            entry["item"] = SITE + href
        items.append(entry)
    return {"@type": "BreadcrumbList", "@id": SITE + slug + "#breadcrumb", "itemListElement": items}


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------
def build_pagehead(meta):
    ph = meta.get("pagehead")
    if not ph:
        return ""
    crumb_html = ['<li><a href="index.html">Home</a></li>']
    for name, href in meta.get("crumbs", []):
        if href:
            crumb_html.append(f'<li><a href="{href}">{name}</a></li>')
        else:
            crumb_html.append(f'<li><span aria-current="page">{name}</span></li>')
    lede = f'\n      <p class="lede">{ph["lede"]}</p>' if ph.get("lede") else ""
    extra = f'\n      {ph["extra"]}' if ph.get("extra") else ""
    return f"""
<section class="pagehead">
  <div class="shell">
    <ol class="breadcrumb">{"".join(crumb_html)}</ol>
    <p class="eyebrow eyebrow--gold">{ph.get("eyebrow", "")}</p>
    <h1>{ph["h1"]}</h1>{lede}{extra}
  </div>
</section>
"""


FRONT = re.compile(r"^(?P<meta>\{.*?\n\})\s*\n---\s*\n(?P<body>.*)$", re.S)


def load_page(path):
    raw = open(path, encoding="utf-8").read()
    m = FRONT.match(raw.lstrip())
    if not m:
        raise SystemExit(f"{path}: missing JSON front-matter followed by a '---' line")
    try:
        meta = json.loads(m.group("meta"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: front-matter is not valid JSON — {e}")
    return meta, m.group("body")


def build():
    base = open(os.path.join(PARTIALS, "base.html"), encoding="utf-8").read()
    files = sorted(f for f in os.listdir(PAGES) if f.endswith(".html"))
    if not files:
        raise SystemExit("No page sources found in _build/pages/")

    written = []
    for fname in files:
        meta, body = load_page(os.path.join(PAGES, fname))
        slug = meta.get("slug", fname)

        graph = [ORGANISATION, WEBSITE]
        if meta.get("event", slug == "index.html"):
            graph.append(EVENT)
        if meta.get("crumbs"):
            graph.append(breadcrumbs(meta["crumbs"], slug))
        graph.extend(meta.get("jsonld", []))
        jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                            ensure_ascii=False, separators=(",", ":"))

        body_class = meta.get("bodyClass", "")
        html = base
        html = html.replace("__TITLE__", meta["title"])
        html = html.replace("__OGTITLE__", meta.get("ogTitle", meta["title"]))
        html = html.replace("__DESCRIPTION__", meta["description"])
        html = html.replace("__SLUG__", "" if slug == "index.html" else slug)
        html = html.replace("__SITE__", SITE)
        html = html.replace("__ROBOTS__", meta.get("robots", "index,follow,max-image-preview:large,max-snippet:-1"))
        html = html.replace("__OGTYPE__", meta.get("ogType", "website"))
        html = html.replace("__HEAD_EXTRA__", meta.get("headExtra", ""))
        html = html.replace("__BODY_CLASS__", f' class="{body_class}"' if body_class else "")
        html = html.replace("__JSONLD__", jsonld)
        html = html.replace("__NAV__", render_nav(meta.get("navKey"), slug))
        html = html.replace("__PAGEHEAD__", build_pagehead(meta))
        html = html.replace("__BODY__", body.strip())
        html = html.replace("__BODY_EXTRA__", meta.get("bodyExtra", ""))
        html = html.replace("__DAYS__", str(DAYS_TO_SUMMIT))

        leftovers = re.findall(r"__[A-Z_]+__", html)
        if leftovers:
            print(f"  ! {slug}: unreplaced tokens {set(leftovers)}", file=sys.stderr)

        with open(os.path.join(ROOT, slug), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        written.append((slug, meta.get("priority", "0.7"), meta.get("changefreq", "monthly"),
                        meta.get("robots", "index")))
        print(f"  · {slug}  ({len(html):,} bytes)")

    write_sitemap(written)
    write_robots()
    write_manifest()
    print(f"\nBuilt {len(written)} pages into {ROOT}")


def write_sitemap(pages):
    urls = []
    for slug, priority, changefreq, robots in sorted(pages, key=lambda p: -float(p[1])):
        if "noindex" in robots:
            continue
        loc = SITE if slug == "index.html" else SITE + slug
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>"
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(xml)


def write_robots():
    txt = f"""# The Healthspan Standard 2027
User-agent: *
Allow: /
Disallow: /dashboard.html
Disallow: /payment.html
Disallow: /_build/

Sitemap: {SITE}sitemap.xml
"""
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(txt)


def write_manifest():
    manifest = {
        "name": "The Healthspan Standard 2027 — Delhi",
        "short_name": "Healthspan 2027",
        "description": "A Constitution for Longevity & Regenerative Medicine. Delhi, 10–11 April 2027.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#F7F0E1",
        "theme_color": "#4E120C",
        "lang": "en-IN",
        "icons": [
            {"src": "assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
            {"src": "assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    build()
