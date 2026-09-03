#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rewrite the generator's INVENTORY array from the inventory CSV.

The equipment catalog lives in two places: the inventory sheet exported to
`DS_Lab_Inventory - Data for contract form.csv`, and the `const INVENTORY`
array inside `index.html`. The running page only reads the array, so editing
the sheet alone changes nothing. This script regenerates the array from the
sheet so the two cannot drift.

Usage, from the repository root:

    python tools/sync-inventory.py            # rewrite the array in place
    python tools/sync-inventory.py --check    # report drift, change nothing

Exits non-zero under --check when the HTML is out of date, so it can be wired
into a pre-commit hook later if that becomes useful.

Expected CSV columns:
    ID, BDI Name, Contract Name, Contract Category,
    Size in inches, Weight in grams, Replacement Value

Rules this encodes (see Rules.txt):
  * Weight is emitted only when the sheet has one. Custom-built drones have no
    authoritative weight, so they print dimensions only (rule 1's exception).
  * Category strings are copied verbatim from the sheet. Drone detection in the
    page matches the word "drone" case-insensitively, and each distinct value
    becomes a filter chip in the form.
  * Chair-approval items are configured in CHAIR_IDS below, not in the sheet,
    because the sheet has no column for it (rule 4a).
"""

from __future__ import print_function

import collections
import csv
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "DS_Lab_Inventory - Data for contract form.csv")
HTML_PATH = os.path.join(ROOT, "index.html")

# Items that always force department chair approval, regardless of borrower
# role or loan value. Add an asset ID here to flag a new one.
CHAIR_IDS = {"0084"}  # 0084 = Artec


def parse_number(raw):
    """Tolerate '$1,234', '1,280.00', '8,999.00' and blanks."""
    text = (raw or "").replace(",", "").replace("$", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def clean(raw):
    return re.sub(r"\s+", " ", (raw or "").strip())


def load_items():
    with io.open(CSV_PATH, encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    items = []
    first_name_for_id = {}
    duplicates = []

    for row in rows:
        raw_id = clean(row.get("ID"))
        name = clean(row.get("Contract Name"))
        if not raw_id or not name:
            continue

        asset_id = raw_id.zfill(4)  # the sheet sometimes drops leading zeros
        if asset_id in first_name_for_id:
            duplicates.append((asset_id, first_name_for_id[asset_id], name))
            continue
        first_name_for_id[asset_id] = name

        item = collections.OrderedDict()
        item["id"] = "bdi-" + asset_id
        item["assetId"] = asset_id
        item["contractName"] = name
        item["category"] = clean(row.get("Contract Category")) or "Other"

        value = parse_number(row.get("Replacement Value"))
        item["replacementValue"] = int(round(value)) if value is not None else 0

        dimensions = clean(row.get("Size in inches"))
        if dimensions:
            item["dimensions"] = dimensions + " in"

        weight = parse_number(row.get("Weight in grams"))
        if weight is not None:
            item["weightGrams"] = int(round(weight))

        if asset_id in CHAIR_IDS:
            item["requiresChairApproval"] = True

        items.append(item)

    items.sort(key=lambda i: (i["category"].lower(), i["contractName"].lower()))
    return items, len(rows), duplicates


def to_js(items):
    lines = []
    for item in items:
        parts = []
        for key, value in item.items():
            if isinstance(value, bool):
                parts.append("%s: true" % key)
            elif isinstance(value, int):
                parts.append("%s: %d" % (key, value))
            else:
                parts.append("%s: %s" % (key, json.dumps(value)))
        lines.append("  { " + ", ".join(parts) + " }")
    return "const INVENTORY = [\n" + ",\n".join(lines) + "\n];"


def report(items, row_count, duplicates):
    categories = collections.Counter(i["category"] for i in items)
    print("%d items from %d sheet rows" % (len(items), row_count))
    print("categories: " + ", ".join(
        "%s=%d" % pair for pair in sorted(categories.items())))

    for asset_id, kept, dropped in duplicates:
        print("  warning: asset %s appears twice -- kept %r, skipped %r"
              % (asset_id, kept, dropped))

    names = collections.Counter(i["contractName"].lower() for i in items)
    for name, count in names.items():
        if count > 1:
            clashing = [i["assetId"] for i in items
                        if i["contractName"].lower() == name]
            print("  warning: %d items print the same contract name %r (%s)"
                  % (count, name, ", ".join(clashing)))


def main():
    check_only = "--check" in sys.argv[1:]

    items, row_count, duplicates = load_items()
    if not items:
        print("error: no usable rows in %s" % CSV_PATH, file=sys.stderr)
        return 2

    report(items, row_count, duplicates)

    html = io.open(HTML_PATH, encoding="utf-8").read()
    match = re.search(r"const INVENTORY = \[.*?\n\];", html, re.S)
    if not match:
        print("error: could not find the INVENTORY array in %s" % HTML_PATH,
              file=sys.stderr)
        return 2

    generated = to_js(items)
    if match.group(0) == generated:
        print("index.html already matches the sheet")
        return 0

    if check_only:
        print("index.html is OUT OF DATE -- "
              "run tools/sync-inventory.py to update it", file=sys.stderr)
        return 1

    updated = html[:match.start()] + generated + html[match.end():]
    io.open(HTML_PATH, "w", encoding="utf-8", newline="\n").write(updated)
    print("updated the INVENTORY array in index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
