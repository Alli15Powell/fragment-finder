# Fragment Finder (FF) & TSV Merger

**Fragment Finder (FF)** is a PyQt5 desktop app for discovering over-represented short RNA fragments in NGS data. Given a read set and a reference FASTA, FF maps reads with a fast Aho–Corasick core (Cython) to build positional coverage across longer RNAs, calls enrichment peaks, and exports clean `.tsv` tables. Plots are rendered with matplotlib inside the GUI.

- **Project homepage / downloads via the Borchert Lab:**  
  https://www.southalabama.edu/biology/borchertlab/

## Features

- Friendly GUI to select inputs, run analysis, visualize peaks, and export results
- Fast Cython extension for pattern matching and sliding computations (`Procedure.pyx`)
- Data-driven peak calling with `scipy.signal.find_peaks`
- RPM normalization, permutation-based p-values, Z-scores
- Exports per-peak `.tsv` with:
  - **miRNA ID**, **Reads per Million (RPM)**, **Peak Start**, **Peak End**,
    **Peak Sequence**, **Permutation P-Value**, **Z-score Rank**,
    **Total Reads in NGS File**, **File Name**
- **TSV Merger** tool to combine multiple FF runs into one table, with optional origin checking

## Quickstart (from source)

> Requires Python 3.10+ and a C/C++ toolchain (e.g., MSVC Build Tools on Windows, or Xcode/clang on macOS, or gcc on Linux).

```bash
# 1) Create & activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Build the Cython extension (produces Procedure.*.pyd/.so)
python setup.py build_ext --inplace

# 4) Run the GUI
python Main.py
