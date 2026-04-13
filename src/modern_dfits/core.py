from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Iterable

from astropy.io import fits


START_PREFIX = "====>"


def _header_lines(path: Path, hdu_index: int, header: fits.Header) -> list[str]:
    lines = [f"{START_PREFIX} {path}[{hdu_index}]"]
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


def dfits_lines(files: Iterable[str], include_extensions: bool, no_primary: bool) -> list[str]:
    output: list[str] = []
    for file_name in files:
        path = Path(file_name)
        with fits.open(path, memmap=True) as hdul:
            if include_extensions:
                start = 1 if no_primary else 0
                indices = range(start, len(hdul))
            else:
                indices = [0]

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
