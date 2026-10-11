#!/usr/bin/env python3
"""Sanity checks over the generated site: links, anchors, structured data, a11y basics."""

import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []
notes = []


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.imgs = [], set(), []
        self.h1 = 0
        self.labels_for, self.inputs = set(), []
        self.open_tags = []
        self.title = ""
        self._in_title = False
        self.buttons_without_text = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("link", "script") and (a.get("href") or a.get("src")):
            self.links.append(a.get("href") or a.get("src"))
        if tag == "img":
            self.imgs.append(a)
        if tag == "h1":
            self.h1 += 1
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        if tag in ("input", "select", "textarea"):
            self.inputs.append(a)
        if tag == "title":
            self._in_title = True
        if tag not in ("meta", "link", "img", "br", "hr", "input", "source", "path",
                       "circle", "rect", "use", "area", "col", "embed", "track", "wbr"):
            self.open_tags.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self.open_tags and self.open_tags[-1] == tag:
            self.open_tags.pop()
        elif tag in self.open_tags:
            while self.open_tags and self.open_tags.pop() != tag:
                pass

    def handle_data(self, data):
        if self._in_title:
            self.title += data


pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
all_ids = {}

# Pass 1 — collect ids per page
scans = {}
for page in pages:
    html = open(os.path.join(ROOT, page), encoding="utf-8").read()
    s = Scan()
    s.feed(html)
    scans[page] = (s, html)
    all_ids[page] = s.ids

# Pass 2 — verify
for page, (s, html) in scans.items():
    where = f"{page}"

    if s.h1 != 1:
        problems.append(f"{where}: expected exactly one <h1>, found {s.h1}")
    if not s.title.strip():
        problems.append(f"{where}: empty <title>")
    elif len(s.title) > 70:
        notes.append(f"{where}: title is {len(s.title)} chars (Google truncates around 60–65)")

    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not desc:
        problems.append(f"{where}: no meta description")
    elif not (110 <= len(desc.group(1)) <= 185):
        notes.append(f"{where}: meta description is {len(desc.group(1))} chars (aim 120–165)")

    # Structured data parses
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            problems.append(f"{where}: JSON-LD does not parse — {e}")

    # Images have alt
    for img in s.imgs:
        if "alt" not in img:
            problems.append(f"{where}: <img src={img.get('src')}> has no alt attribute")

    # Form controls are labelled
    for inp in s.inputs:
        if inp.get("type") in ("hidden", "submit", "button", "radio", "checkbox", "file"):
            continue
        iid = inp.get("id")
        if not iid:
            problems.append(f"{where}: form control with no id (name={inp.get('name')})")
        elif iid not in s.labels_for and not inp.get("aria-label"):
            problems.append(f"{where}: control #{iid} has no <label for> and no aria-label")

    # Unclosed tags
    if s.open_tags:
        problems.append(f"{where}: unclosed tags {s.open_tags[:6]}")

    # Links resolve
    for href in s.links:
        if href.startswith(("http://", "https://", "mailto:", "tel:", "data:", "//")):
            continue
        target, _, frag = href.partition("#")
        if not target:
            if frag and frag not in s.ids:
                problems.append(f"{where}: in-page anchor #{frag} has no matching id")
            continue
        path = os.path.join(ROOT, target)
        if not os.path.exists(path):
            problems.append(f"{where}: link target missing — {target}")
        elif frag and target.endswith(".html") and frag not in all_ids.get(target, set()):
            problems.append(f"{where}: {target}#{frag} — no element with that id on the target page")

# Orphan check: every page reachable from somewhere
linked = set()
for page, (s, _) in scans.items():
    for href in s.links:
        t = href.partition("#")[0]
        if t.endswith(".html"):
            linked.add(t)
for page in pages:
    if page not in linked and page not in ("index.html", "404.html"):
        notes.append(f"{page}: not linked from any other page")

print(f"Checked {len(pages)} pages\n")
if problems:
    print(f"PROBLEMS ({len(problems)})")
    for p in problems:
        print("  X " + p)
else:
    print("No problems found.")
if notes:
    print(f"\nNOTES ({len(notes)})")
    for n in notes:
        print("  - " + n)

sys.exit(1 if problems else 0)
