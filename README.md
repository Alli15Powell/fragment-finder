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
TSV Merger
Run interactively:

bash
Copy code
python TSV-Merger.py
# Prompts:
#  - Directory containing FF .tsv files
#  - Database FASTA used for alignment
#  - Which files to include
#  - Output filename
# Output: Joined_Results/<name>.tsv and optionally <name>_checked.tsv
Annotate a merged file directly (CLI):

bash
Copy code
python check_origins.py -m path/to/merged.tsv -d path/to/database.fasta -o path/to/merged_checked.tsv
Packaging the GUI (optional)
To build a Windows executable with your existing .spec:

bash
Copy code
pyinstaller FragmentFinder.spec
Or build from scratch:

bash
Copy code
pyinstaller --onefile --windowed --add-data "loading.gif;." Main.py
On macOS/Linux, replace the semicolon (;) with a colon (:) in --add-data.

Repository layout (suggested)
graphql
Copy code
fragment-finder/
├─ src/                      # GUI + Cython
│  ├─ Main.py
│  ├─ Util.py
│  ├─ Procedure.pyx
│  ├─ setup.py
│  └─ loading.gif
├─ tools/                    # utilities
│  ├─ TSV-Merger.py
│  └─ check_origins.py
├─ data/                     # sample inputs/outputs (gitignored)
│  └─ .gitkeep
├─ requirements.txt
└─ README.md
Contributing
Issues and PRs are welcome—especially improvements to documentation, tests, cross-platform builds, and UI/UX. Consider adding CI (GitHub Actions) to build the Cython module on Windows/macOS/Linux.

License
GPL. See LICENSE for details.

Acknowledgments
Borchert Lab, University of South Alabama — hosting, collaboration, and downloads:
https://www.southalabama.edu/biology/borchertlab/

Open-source tools that make this possible: Python, PyQt5, Cython, NumPy/SciPy, matplotlib, Biopython, pyahocorasick.

perl
Copy code
::contentReference[oaicite:0]{index=0}
 ​:contentReference[oaicite:1]{index=1}​
