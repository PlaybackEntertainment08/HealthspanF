#!/usr/bin/env bash
# Drive the QA harness across pages x viewports with headless Chrome.
# Usage: bash _build/qa.sh [width] [height] [page ...]
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
BASE="http://127.0.0.1:8099"
W="${1:-1440}"; H="${2:-900}"
shift 2 2>/dev/null
ALL="index.html programme.html registration.html login.html dashboard.html payment.html charter.html longevity-40.html abstracts.html faq.html sponsors.html accommodation.html visa.html contact.html committee.html experience-lounge.html terms.html nominate.html tour.html venue.html workshops.html faculty.html books.html about.html downloads.html rapid-fire.html privacy.html 404.html organisers.html advisory-board.html collaborations.html allied-health.html industry-workshop.html"
PAGES="${*:-$ALL}"

# The harness must be same-origin with the pages, so it is copied into the
# site root for the run and removed afterwards. It is never deployed.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp "$ROOT/_build/qa-harness.html" "$ROOT/_qa.html"
trap 'rm -f "$ROOT/_qa.html"' EXIT

for p in $PAGES; do
  res=$("$CHROME" --headless=new --disable-gpu --virtual-time-budget=9000 --dump-dom \
        --window-size=$((W+40)),$((H+140)) \
        "$BASE/_qa.html?page=$p&w=$W&h=$H" 2>/dev/null \
        | grep -o 'QA::[^<]*' | head -1 \
        | sed 's/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g; s/^QA:://')
  if [ -z "$res" ]; then
    printf '  ????  %-24s (harness produced no result)\n' "$p"
  elif [ "$res" = "CLEAN" ]; then
    printf '  ok    %-24s\n' "$p"
  else
    printf '  ISSUE %-24s %s\n' "$p" "$res"
  fi
done
