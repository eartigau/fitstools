from __future__ import annotations

import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

from astropy.io import fits


START_PREFIX = "====>"


def _header_lines(path: Path, hdu_index: int, header: fits.Header) -> list[str]:
    suffix = f"[{hdu_index}]" if hdu_index != 0 else ""
    lines = [f"{START_PREFIX} {path}{suffix}"]
    for card in header.cards:
        # Keep formatting compact and stable for downstream parsing.
        key = (card.keyword or "").strip()
        value = card.value
        comment = (card.comment or "").strip()

        if key == "":
            continue

        value_text = _value_to_text(value)
        if comment:
            lines.append(f"{key} = {value_text} / {comment}")
        else:
            lines.append(f"{key} = {value_text}")

    return lines


def _value_to_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, bool):
        return "T" if value else "F"
    return str(value)


ALL_EXTENSIONS = "all"


def _select_hdus(hdul: fits.HDUList, extension: str | None, no_primary: bool) -> list[int]:
    if extension is None:
        return [0]

    # As in ESO dfits, `-x 0` means every HDU.
    if extension in (ALL_EXTENSIONS, "0"):
        start = 1 if no_primary else 0
        return list(range(start, len(hdul)))

    if extension.isdigit():
        index = int(extension)
        if index >= len(hdul):
            raise KeyError(f"no extension {index} (file has {len(hdul)} HDUs)")
        return [index]

    # EXTNAME lookup is case-insensitive in astropy.
    try:
        return [hdul.index_of(extension)]
    except KeyError:
        raise KeyError(f"no extension named {extension!r}") from None


def dfits_lines(
    files: Iterable[str],
    extension: str | None = None,
    no_primary: bool = False,
) -> list[str]:
    """Header lines for each file.

    extension: None for the primary header only, "all" (or "0") for every
    HDU, otherwise one HDU given by its index or its EXTNAME. Files lacking
    the requested extension are skipped with a warning on stderr.
    """
    output: list[str] = []
    for file_name in files:
        path = Path(file_name)
        with fits.open(path, memmap=True) as hdul:
            try:
                indices = _select_hdus(hdul, extension, no_primary)
            except KeyError as exc:
                print(f"dfits: warning: {path}: {exc.args[0]}, skipped", file=sys.stderr)
                continue

            for hdu_index in indices:
                output.extend(_header_lines(path, hdu_index, hdul[hdu_index].header))

    return output


def parse_dfits_stream(lines: Iterable[str]) -> list[tuple[str, dict[str, str]]]:
    records: list[tuple[str, dict[str, str]]] = []
    current_name: str | None = None
    current_header: OrderedDict[str, str] | None = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue

        if line.startswith(START_PREFIX):
            if current_name is not None and current_header is not None:
                records.append((current_name, dict(current_header)))

            current_name = line[len(START_PREFIX) :].strip()
            current_header = OrderedDict()
            continue

        if current_header is None:
            continue

        if "=" not in line:
            continue

        key_part, rhs = line.split("=", 1)
        key = key_part.strip().upper()
        value = rhs.strip()
        if " / " in value:
            value = value.split(" / ", 1)[0].strip()

        current_header[key] = value

    if current_name is not None and current_header is not None:
        records.append((current_name, dict(current_header)))

    return records
