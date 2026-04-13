from __future__ import annotations

import argparse
import csv
import sys

from .core import parse_dfits_stream


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fitsort",
        description="Extract selected FITS keywords from dfits stream.",
    )
    parser.add_argument("keywords", nargs="+", help="Header keywords to extract")
    parser.add_argument(
        "-s",
        "--separator",
        default=" ",
        help="Output separator for plain text mode",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Emit CSV output",
    )
    parser.add_argument(
        "--missing",
        default="-",
        help="Placeholder used when keyword is missing",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    records = parse_dfits_stream(sys.stdin)
    if not records:
        print("fitsort: no input records found on stdin", file=sys.stderr)
        return 1

    keywords = [k.upper() for k in args.keywords]
    header = ["FILE"] + keywords

    if args.csv:
        writer = csv.writer(sys.stdout)
        writer.writerow(header)
        for name, cards in records:
            row = [name] + [cards.get(k, args.missing) for k in keywords]
            writer.writerow(row)
        return 0

    sep = args.separator
    rows = [header]
    for name, cards in records:
        rows.append([name] + [cards.get(k, args.missing) for k in keywords])
    
    # Calculate column widths
    widths = [max(len(r[i]) for r in rows) for i in range(len(header))]
    
    # Detect if each column is numeric
    def is_numeric(s: str) -> bool:
        s = s.strip()
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    is_numeric_col = []
    for col_idx in range(len(header)):
        numeric_count = sum(1 for row in rows[1:] if is_numeric(row[col_idx]))
        is_numeric_col.append(numeric_count == len(rows) - 1 and len(rows) > 1)
    
    # Format and print rows
    for row in rows:
        padded = []
        for i, cell in enumerate(row):
            if is_numeric_col[i]:
                padded.append(cell.rjust(widths[i]))
            else:
                padded.append(cell.ljust(widths[i]))
        # strip trailing whitespace on last column
        padded[-1] = padded[-1].rstrip()
        print(sep.join(padded))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
