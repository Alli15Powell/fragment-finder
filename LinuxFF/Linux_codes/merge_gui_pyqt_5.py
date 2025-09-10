#!/usr/bin/env python3
"""
TSV Merger GUI (PyQt5)
----------------------
A clean PyQt5 GUI wrapper for your TSV-merging pipeline.

It expects a companion module named `merge_core.py` in the same folder
that exposes the following functions (adapt names if yours differ):
  - get_files(dir_path) -> list[str]
  - get_new_out_file_name(file_list) -> str
  - get_list_count(file_list) -> int
  - merge_files(dir_path) -> None
  - init_group() -> None
  - get_orig_strings(fasta_path) -> dict
  - get_final_group(hmap: dict) -> None
  - export_final_csv(file_count: int, out_file: str) -> None

Build (Linux, PyQt5):
  # optional: create a clean env
  # conda create -n merger-pyqt5 python=3.10 pyqt biopython pandas pyinstaller -y
  # conda activate merger-pyqt5

  pyinstaller --onefile --windowed --name TSV_Merger_linux \
    --collect-all PyQt5 \
    --hidden-import Bio.SeqIO --collect-submodules Bio \
    --exclude-module PySide6 --exclude-module shiboken6 \
    merge_gui_pyqt5.py

Run:
  ./dist/TSV_Merger_linux

Notes:
- Keep `merge_core.py` in the same folder as this GUI file.
- If your core needs extra data files, add them via --add-data "src:dest" (Linux uses ':').
- This GUI logs progress, keeps the UI responsive, and surfaces full tracebacks on failure.
"""
from __future__ import annotations

import os
import sys
import traceback
from dataclasses import dataclass

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot

# --- Import your core pipeline ---
try:
    import merge_core as core  # rename your base script to merge_core.py if needed
except Exception as e:
    core = None
    _import_error = e
else:
    _import_error = None


# -------------------------- Worker (runs off the UI thread) --------------------------
class MergeWorker(QtCore.QObject):
    started = Signal()
    log = Signal(str)
    progressed = Signal(int)  # 0..100
    finished = Signal(str)    # final output path
    failed = Signal(str)      # error text (traceback)

    def __init__(self, dir_path: str, fasta_path: str):
        super().__init__()
        self.dir_path = dir_path
        self.fasta_path = fasta_path

    @Slot()
    def run(self):
        try:
            self.started.emit()
            self.progressed.emit(1)

            if core is None:
                raise RuntimeError(f"Could not import merge_core: {_import_error}")

            if not os.path.isdir(self.dir_path):
                raise ValueError("Please select a valid directory containing .tsv/.csv files.")
            if not os.path.isfile(self.fasta_path):
                raise ValueError("Please select a valid FASTA database file.")

            os.makedirs("tmp", exist_ok=True)
            os.makedirs("Joined_Outputs", exist_ok=True)

            self.log.emit("Scanning input directory…")
            files = core.get_files(self.dir_path)
            if not files:
                raise ValueError("No input files found in the selected directory.")
            out_file = core.get_new_out_file_name(files)
            file_count = core.get_list_count(files)

            self.progressed.emit(10)
            self.log.emit(f"Found {len(files)} files. Merging…")
            core.merge_files(self.dir_path)

            self.progressed.emit(40)
            self.log.emit("Grouping peaks…")
            core.init_group()

            self.progressed.emit(55)
            self.log.emit("Loading FASTA database (Bio.SeqIO)…")
            hmap = core.get_orig_strings(self.fasta_path)

            self.progressed.emit(70)
            self.log.emit("Computing final groups…")
            core.get_final_group(hmap)

            self.progressed.emit(85)
            self.log.emit("Exporting final CSV…")
            core.export_final_csv(file_count, out_file)

            # best-effort cleanup
            for p in ["tmp/files_and_reads.csv", "tmp/grouped_by_peak.csv", "tmp/t1.csv"]:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass

            final_path = os.path.abspath(os.path.join("Joined_Outputs", f"{out_file}.csv"))
            self.progressed.emit(100)
            self.log.emit(f"✅ Done! Output: {final_path}")
            self.finished.emit(final_path)

        except Exception:
            tb = traceback.format_exc()
            self.failed.emit(tb)


# --------------------------------- Main Window UI ---------------------------------
@dataclass
class Paths:
    data_dir: str = ""
    fasta: str = ""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSV Merger — Consensus Peaks")
        self.resize(920, 560)

        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Top form
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignLeft)
        layout.addLayout(form)

        # Input directory
        self.dir_edit = QtWidgets.QLineEdit()
        self.dir_edit.setPlaceholderText("Directory containing .tsv/.csv files…")
        self.dir_btn = QtWidgets.QPushButton("Browse…")
        self.dir_btn.clicked.connect(self.pick_dir)
        dir_row = QtWidgets.QHBoxLayout()
        dir_row.addWidget(self.dir_edit)
        dir_row.addWidget(self.dir_btn)
        form.addRow("Input directory:", dir_row)

        # FASTA database file
        self.fasta_edit = QtWidgets.QLineEdit()
        self.fasta_edit.setPlaceholderText("FASTA database file (e.g., .fa, .fasta, .fna)…")
        self.fasta_btn = QtWidgets.QPushButton("Browse…")
        self.fasta_btn.clicked.connect(self.pick_fasta)
        fasta_row = QtWidgets.QHBoxLayout()
        fasta_row.addWidget(self.fasta_edit)
        fasta_row.addWidget(self.fasta_btn)
        form.addRow("FASTA database:", fasta_row)

        # Run + progress
        run_row = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("Run Merge")
        self.run_btn.setDefault(True)
        self.run_btn.clicked.connect(self.start_run)
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        run_row.addWidget(self.run_btn)
        run_row.addWidget(self.progress, 1)
        layout.addLayout(run_row)

        # Log view
        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.log_view.setFont(font)
        layout.addWidget(self.log_view, 1)

        # Status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

        self.paths = Paths()
        self._thread: QtCore.QThread | None = None
        self._worker: MergeWorker | None = None

        if _import_error:
            self.append_log(f"⚠️ merge_core import error: {_import_error}")
            self.status.showMessage("merge_core import error — see log")

    # ------------- UI helpers -------------
    def append_log(self, text: str):
        self.log_view.appendPlainText(text)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )

    def pick_dir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select directory with .tsv/.csv files")
        if d:
            self.paths.data_dir = d
            self.dir_edit.setText(d)

    def pick_fasta(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select FASTA database",
            "",
            "FASTA files (*.fa *.fasta *.fna *.fas);;All files (*)",
        )
        if f:
            self.paths.fasta = f
            self.fasta_edit.setText(f)

    # ------------- Run pipeline -------------
    def start_run(self):
        self.paths.data_dir = self.dir_edit.text().strip()
        self.paths.fasta = self.fasta_edit.text().strip()

        if not self.paths.data_dir:
            QtWidgets.QMessageBox.warning(self, "Missing directory", "Please select the input directory.")
            return
        if not self.paths.fasta:
            QtWidgets.QMessageBox.warning(self, "Missing FASTA", "Please select the FASTA database file.")
            return

        self.run_btn.setEnabled(False)
        self.progress.setValue(0)
        self.append_log("▶️ Starting…")
        self.status.showMessage("Running…")

        self._thread = QtCore.QThread(self)
        self._worker = MergeWorker(self.paths.data_dir, self.paths.fasta)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.started.connect(lambda: self.progress.setValue(1))
        self._worker.log.connect(self.append_log)
        self._worker.progressed.connect(self.progress.setValue)
        self._worker.finished.connect(self.on_finished)
        self._worker.failed.connect(self.on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self.cleanup_thread)

        self._thread.start()

    @Slot(str)
    def on_finished(self, final_path: str):
        self.run_btn.setEnabled(True)
        self.status.showMessage("Done")
        QtWidgets.QMessageBox.information(self, "Merge Complete", f"Output written to:\n{final_path}")

    @Slot(str)
    def on_failed(self, err_text: str):
        self.run_btn.setEnabled(True)
        self.status.showMessage("Failed — see log")
        self.append_log("\n❌ ERROR TRACEBACK:\n" + err_text)
        QtWidgets.QMessageBox.critical(self, "Error", "An error occurred. See the log for details.")

    @Slot()
    def cleanup_thread(self):
        self._worker = None
        self._thread = None


# --------------------------------- App entrypoint ---------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("TSV Merger")
    app.setOrganizationName("FragmentFinder")

    w = MainWindow()
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
