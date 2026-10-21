from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .core import ALL_EXTENSIONS, dfits_lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dfits",
        description="Print FITS headers in a dfits-compatible stream.",
    )
    parser.add_argument("files", nargs="*", help="FITS files to inspect")
    parser.add_argument(
        "-x",
        "--extensions",
        nargs="?",
        const=ALL_EXTENSIONS,
        default=None,
        metavar="EXT",
        help=(
            "Include extension headers. Alone (or as -x 0), print all HDUs; "
            "with an index (-x 1) or an EXTNAME (-x FluxA), print only that HDU"
        ),
    )
    parser.add_argument(
        "-n",
        "--no-primary",
        action="store_true",
        help="When printing all HDUs with --extensions, skip primary header",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # `dfits -x file.fits` (bare -x before a file) makes argparse take the file
    # as the extension; give it back to the file list.
    if args.extensions not in (None, ALL_EXTENSIONS) and Path(args.extensions).is_file():
        args.files.insert(0, args.extensions)
        args.extensions = ALL_EXTENSIONS

    if not args.files:
        parser.error("the following arguments are required: files")

    try:
        lines = dfits_lines(
            files=args.files,
            extension=args.extensions,
            no_primary=args.no_primary,
        )
    except Exception as exc:
        print(f"dfits: error: {exc}", file=sys.stderr)
        return 1

    try:
        for line in lines:
            print(line)
    except BrokenPipeError:
        # Reader closed early (e.g. `| head`); silence the flush at exit.
        sys.stdout = open(os.devnull, "w")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
