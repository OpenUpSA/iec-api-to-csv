"""Convert the IEC's certified candidate list PDF into a CSV.

The PDF is an Excel sheet printed to PDF, so every page has the same fixed
column layout. Each text span is a cell, placed into a column by its x position
and into a row by its y position.

    python convert-candidate-list-pdf-to-csv.py [PDF] [CSV]
"""

import csv
import os
import re
import sys
from collections import defaultdict

import pymupdf

DEFAULT_PDF = "data/LGE2026 Certified Candidates List_16092026.pdf"
DEFAULT_CSV = "output/pre-election/1887/certified-candidates.csv"

# Left edge of each column, from the header row. The order number is right
# aligned, so its column starts where the party column's widest text ends.
COLUMNS = [
    ("Province", 0),
    ("Municipality", 125),
    ("Party", 238),
    ("WardOrListOrder", 428),
    ("IDNumber", 478),
    ("Fullname", 534),
    ("Surname", 666),
]
# Page title and column headings sit above this
BODY_TOP = 58
# Printed on the same line as the last row of each page
FOOTER = re.compile(r"Page \d+ of \d+")

FIELDNAMES = [
    "Province",
    "Municipality",
    "Party",
    "CandidateType",
    "WardID",
    "ListOrder",
    "IDNumber",
    "Fullname",
    "Surname",
]


def column_for(x):
    for name, left in reversed(COLUMNS):
        if x >= left:
            return name


def rows_on_page(page):
    lines = defaultdict(lambda: defaultdict(list))
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                x0, y0, x1, y1 = span["bbox"]
                text = span["text"].strip()
                if text and y0 >= BODY_TOP and not FOOTER.fullmatch(text):
                    lines[round(y1)][column_for(x0)].append((x0, text))

    for _, cells in sorted(lines.items()):
        row = {
            name: " ".join(text for _, text in sorted(cells[name]))
            for name, _ in COLUMNS
        }
        missing = [name for name, value in row.items() if not value]
        if missing:
            # A few rows in the source have no name; keep them, but say so
            print(f"Page {page.number + 1}: row missing {missing}: {row}")
        yield row


def candidate(row):
    # The PDF shares one column between ward IDs (8 digits) and PR list order
    order = row.pop("WardOrListOrder")
    if len(order) == 8:
        return {**row, "CandidateType": "Ward", "WardID": order, "ListOrder": ""}
    return {**row, "CandidateType": "PR", "WardID": "", "ListOrder": order}


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    csv_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CSV

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    count = 0
    with pymupdf.open(pdf_path) as pdf, open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for page in pdf:
            for row in rows_on_page(page):
                writer.writerow(candidate(row))
                count += 1

    print(f"Wrote {count} candidates from {pdf_path} to {csv_path}")


if __name__ == "__main__":
    main()
