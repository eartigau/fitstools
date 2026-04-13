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
    widths = [max(len(r[i]) for r in rows) for i in range(len(header))]
    for row in rows:
        padded = [cell.ljust(widths[i]) for i, cell in enumerate(row)]
        # strip trailing whitespace on last column
        padded[-1] = padded[-1].rstrip()
        print(sep.join(padded))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
