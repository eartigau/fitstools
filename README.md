# modern-dfits

A modern Python replacement for ESO `dfits` and `fitsort`.

This project provides two command-line tools:

- `dfits`: reads FITS files and emits a text stream containing header cards.
- `fitsort`: reads that stream and prints selected FITS keywords in a table.

The tools are designed to be used together, matching the classic workflow:

```bash
dfits *.fits | fitsort OBJECT DATE-OBS EXPTIME
```

## Install

Requirements:

- Python 3.10 or newer
- `pip`

On macOS with Homebrew Python, `python3 -m pip install ...` may fail with `externally-managed-environment` (PEP 668). Install into an active conda environment instead:

```bash
conda activate <your-env>
pip install git+https://github.com/eartigau/fitstools.git
```

If you don't have a conda environment yet:

```bash
conda create -n fitstools python=3.12
conda activate fitstools
pip install git+https://github.com/eartigau/fitstools.git
```

Install from a local clone:

```bash
git clone https://github.com/eartigau/fitstools.git
cd fitstools
python -m pip install .
```

For development, install in editable mode:

```bash
git clone https://github.com/eartigau/fitstools.git
cd fitstools
python -m pip install -e .
```

After installation, the `dfits` and `fitsort` commands should be available in your shell. You can verify that with:

```bash
dfits --help
fitsort --help
```

## Usage

### `dfits`

```bash
dfits file1.fits file2.fits
dfits -x file.fits
```

Options:

- `-x`, `--extensions`: include extension-level headers (all HDUs). Default behavior prints only primary header (HDU 0).
- `-n`, `--no-primary`: when `--extensions` is set, skip primary header and print only extension headers.

### `fitsort`

```bash
dfits *.fits | fitsort OBJECT DATE-OBS EXPTIME
```

Options:

- `-s`, `--separator`: output separator (default: single space).
- `--csv`: emit CSV output.
- `--missing`: placeholder for missing keys (default: `-`).

`fitsort` expects input from `dfits` on stdin.

## Notes

- This is a practical compatibility layer, not a byte-for-byte clone of ESO output formatting.
- Keyword lookup is case-insensitive.
