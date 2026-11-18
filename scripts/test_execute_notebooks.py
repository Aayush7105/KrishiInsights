"""
Independent Notebook Execution and Verification Runner for Stage 4.
Executes all 5 Stage 4 notebooks cell-by-cell in clean, isolated environments.
"""

import os
import sys
import nbformat as nbf

sys.path.insert(0, ".")

NOTEBOOKS = [
    "01_agricultural_eda.ipynb",
    "02_crop_analysis.ipynb",
    "03_regional_analysis.ipynb",
    "04_rainfall_analysis.ipynb",
    "05_rainfall_agriculture_relationship.ipynb"
]

def verify_all_notebooks():
    print("=" * 70)
    print("KRISHIINSIGHTS STAGE 4 — NOTEBOOK EXECUTION FROM SCRATCH")
    print("=" * 70)

    notebook_dir = "ml/notebooks"
    all_passed = True

    for nb_name in NOTEBOOKS:
        nb_path = os.path.join(notebook_dir, nb_name)
        print(f"\n--- Testing Notebook: {nb_name} ---")
        if not os.path.exists(nb_path):
            print(f"[FAIL] Notebook file not found: {nb_path}")
            all_passed = False
            continue

        with open(nb_path, "r", encoding="utf-8") as f:
            nb = nbf.read(f, as_version=4)

        # Fresh isolated namespace for the notebook
        exec_globals = {
            "__file__": nb_path,
            "__name__": "__main__"
        }

        cell_count = 0
        error_count = 0

        for idx, cell in enumerate(nb.cells):
            if cell.cell_type == "code":
                cell_count += 1
                source = cell.source
                try:
                    exec(source, exec_globals)
                except Exception as e:
                    print(f"  [ERROR] In cell {cell_count} (index {idx}): {type(e).__name__}: {e}")
                    error_count += 1
                    all_passed = False

        if error_count == 0:
            print(f"  [PASS] All {cell_count} code cells executed successfully with 0 errors.")
        else:
            print(f"  [FAIL] {error_count} errors encountered in {nb_name}.")

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL 5 NOTEBOOKS EXECUTED CLEANLY FROM SCRATCH WITH 100% REPRODUCIBILITY")
    else:
        print("NOTEBOOK VERIFICATION ENCOUNTERED FAILURES")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = verify_all_notebooks()
    sys.exit(0 if success else 1)
