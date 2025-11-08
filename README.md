# IBM-Applied-Data-Science-Capstone---SpaceX-Project

## Summary
This package contains the cleaned dataset, a corrected Dash application, and supporting files to ensure reproducibility and clarity. Changes applied:
- Removed accidental index column (`Unnamed:...`) from the CSV.
- Cleaned `Mission Outcome` textual labels (removed parenthetical notes).
- Updated Dash app to use **inclusive** payload filtering (`>=` / `<=`) so slider endpoints are included.
- Pie chart now shows human-readable labels ('Success' / 'Failure').
- Added `requirements.txt` listing dependencies.

## Files in this ZIP
- `spacex_launch_dash_clean.csv` — cleaned CSV (no Unnamed index; mission outcome cleaned)
- `spacex_dash_app_fixed.py` — corrected Dash app (inclusive filter, readable pie labels, improved slider marks)
- `requirements.txt` — minimal requirements for running notebooks and the Dash app
- `README_expanded.md` — this file

## How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the Dash app (ensure `spacex_launch_dash_clean.csv` is in same folder):
   ```bash
   python spacex_dash_app_fixed.py
   ```
3. Open the app at `http://127.0.0.1:8050/`
