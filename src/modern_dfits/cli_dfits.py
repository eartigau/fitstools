from __future__ import annotations

import argparse
import sys

from .core import dfits_lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dfits",
        description="Print FITS headers in a dfits-compatible stream.",
    )
    parser.add_argument("files", nargs="+", help="FITS files to inspect")
    parser.add_argument(
        "-x",
        "--extensions",
        action="store_true",
        help="Include all HDUs (extensions) instead of only primary header",
    )
    parser.add_argument(
        "-n",
        "--no-primary",
        action="store_true",
        help="When using --extensions, skip primary header",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        lines = dfits_lines(
            files=args.files,
            include_extensions=args.extensions,
            no_primary=args.no_primary,
        )
    except Exception as exc:
        print(f"dfits: error: {exc}", file=sys.stderr)
        return 1

    for line in lines:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
