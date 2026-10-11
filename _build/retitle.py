#!/usr/bin/env python3
"""One-off: rewrite page titles and meta descriptions to SERP-friendly lengths.

Titles aim for 55-62 characters, descriptions for 135-160, with the primary
keyword phrase front-loaded. Run once; after this, edit the front-matter
in _build/pages/ directly.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, "pages")

COPY = {
"index.html": (
 "Healthspan Standard 2027 — Longevity Summit, Delhi",
 "An evidence-led longevity and regenerative medicine summit in New Delhi, 10–11 April 2027. 36 lectures, the Longevity 40 honours, and a Charter signed in Delhi."),
"about.html": (
 "Why We Gather — The Case for a Healthspan Standard",
 "The lifespan–healthspan gap averaged 9.6 years and is widening. Why this Delhi summit puts evidence before enthusiasm, who it is for, and what it leaves behind."),
"charter.html": (
 "The Charter — Consensus Statements, Delhi 2027",
 "Twelve draft consensus statements on evidence, consent, advertising, regulation and access — read, argued, amended and signed in Delhi on 11 April 2027."),
"books.html": (
 "Three Books, Unveiled From the Stage | Delhi 2027",
 "The Healthspan Standard, Regenerative Intelligence and The 10 PM Club — each launched from the stage with a reading and a conversation with the authors."),
"committee.html": (
 "Organising & Scientific Committee | Delhi 2027",
 "The patrons, organising team, scientific committee and independent Longevity 40 jury — and the governance rules that keep the programme apart from its sponsors."),
"faculty.html": (
 "National & International Faculty | Delhi 2027",
 "Session chairs and lecturers for the Healthspan Standard 2027 summit, invited by the scientific committee and announced in stages from December 2026."),
"venue.html": (
 "Venue & Getting There — New Delhi, April 2027",
 "Venue details, hall layout, accessibility and how to reach Aerocity from Indira Gandhi International Airport — plus what Delhi is actually like in April."),
"programme.html": (
 "Scientific Programme — 11 Sessions, 36 Lectures",
 "The full two-day programme: eleven sessions, thirty-six lectures, three panels, three book launches and the adoption of the Charter. Every slide carries its tier."),
"rapid-fire.html": (
 "Rapid-Fire Rounds — 30 Talks of Six Minutes",
 "Five rounds of 45 minutes in Hall II on Day Two: measuring ageing, the Indian plate, regenerative practice, traditions under the evidence lens, women’s healthspan."),
"workshops.html": (
 "Pre-Summit Workshops & Masterclasses, 9 April",
 "Hands-on workshops the day before the summit: regenerative skills and ultrasound-guided injection, the longevity consultation, point-of-care assessment, trainees."),
"experience-lounge.html": (
 "The Experience Lounge — Eight Assessment Stations",
 "Try the tests you order for your patients. Eight stations — biological age, VO₂, HRV, grip strength, sleep — each showing the evidence tier behind its claim."),
"abstracts.html": (
 "Abstracts & Submissions — Close 31 January 2027",
 "Submit an abstract for Delhi 2027. Nine categories across rapid-fire oral, e-poster, video, allied health and the Research Excellence Award. Evidence tier required."),
"longevity-40.html": (
 "The Longevity 40 — Inaugural Honours, Delhi 2027",
 "Forty clinicians, scientists, innovators and organisations honoured for evidence-based work. Eleven categories, an independent panel, no entry fee, never purchased."),
"nominate.html": (
 "Nominate for the Longevity 40 — Free and Open",
 "Nominate a colleague for the inaugural Longevity 40 honours in Delhi. Eleven categories, no entry fee, open to anyone. Nominations close 31 January 2027."),
"registration.html": (
 "Registration & Delegate Fees | Delhi, April 2027",
 "Delegate, couple, group, residential, trainee and allied health passes in INR and USD, with early, standard and late rates, full inclusions and the refund policy."),
"login.html": (
 "Delegate Login & Sign Up | Healthspan Standard 2027",
 "Sign in to your delegate profile or create one to register for the Delhi summit. Manage your pass, abstracts, invoices, visa letter and hotel in one place."),
"dashboard.html": (
 "Delegate Dashboard | Healthspan Standard 2027",
 "Your registration status, invoices, abstract submissions, visa letter requests, accommodation, Longevity 40 nominations and personal programme."),
"payment.html": (
 "Secure Checkout — Delegate Payment | Delhi 2027",
 "Complete your delegate registration. Pay by card, UPI, net banking, NEFT or SWIFT. Card details are handled by the gateway and never touch this site."),
"accommodation.html": (
 "Accommodation — Partner Hotels in Aerocity, Delhi",
 "Five-star and four-star partner hotels in Aerocity, within walking distance of the venue and three kilometres from the airport. Residential packages available."),
"visa.html": (
 "Visa & Travel — e-Business Visa (e-B5V) Guidance",
 "How international delegates obtain an Indian visa for the Delhi summit: the e-B5V route, what we need from you, the invitation letter, Ministry approvals, timings."),
"tour.html": (
 "Delhi Tours & the Agra Extension | Delhi 2027",
 "Optional day tours of Old and New Delhi, a Mughal monuments walk, a food trail and the Agra sunrise extension, for delegates and accompanying persons."),
"sponsors.html": (
 "Industry Partners & Sponsorship | Delhi 2027",
 "Partners of the Healthspan Standard 2027 summit and the sponsorship packages available — with the published rules that keep the programme independent of funders."),
"downloads.html": (
 "Downloads — Brochures, Programme & Templates",
 "The delegate brochure, trade brochure, programme PDF, abstract template, the slide template carrying the evidence-tier mark, and the draft Charter statements."),
"faq.html": (
 "Frequently Asked Questions | Delhi, April 2027",
 "Answers on who may attend, fees and inclusions, GST and invoicing, cancellation and transfers, abstracts, the Longevity 40, visas, CME credit and accessibility."),
"contact.html": (
 "Contact the Secretariat | Healthspan Standard 2027",
 "Reach the conference secretariat in New Delhi about registration, abstracts, visa letters, accommodation, sponsorship or press. Answered within one working day."),
"terms.html": (
 "Terms, Cancellation & Refund Policy | Delhi 2027",
 "Terms of registration: eligibility, fees and taxes, the cancellation and refund schedule, transfers, visa refusal, programme changes, conduct and liability."),
"privacy.html": (
 "Privacy Notice | Healthspan Standard 2027",
 "What delegate data we collect and why, who sees it, how long we keep it, and the rights you hold over it — including Experience Lounge measurements."),
"404.html": (
 "Page Not Found | Healthspan Standard 2027",
 "That page does not exist on this site. Find the programme, registration, abstracts, the Longevity 40 and the Charter from the index below."),
}

FRONT = re.compile(r"^(?P<meta>\{.*?\n\})\s*\n---\s*\n(?P<body>.*)$", re.S)

for fname in sorted(os.listdir(PAGES)):
    if not fname.endswith(".html"):
        continue
    path = os.path.join(PAGES, fname)
    raw = open(path, encoding="utf-8").read()
    m = FRONT.match(raw.lstrip())
    meta = json.loads(m.group("meta"))
    slug = meta.get("slug", fname)
    if slug not in COPY:
        print(f"  ? no copy for {slug}")
        continue
    title, desc = COPY[slug]
    meta["ogTitle"] = meta.get("ogTitle", title)
    meta["title"] = title
    meta["description"] = desc
    out = json.dumps(meta, ensure_ascii=False, indent=2) + "\n---\n" + m.group("body")
    open(path, "w", encoding="utf-8", newline="\n").write(out)
    print(f"  . {slug}  title {len(title)}  desc {len(desc)}")
