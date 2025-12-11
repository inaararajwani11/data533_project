The Analytics subpackage transforms focus sessions and habits into weekly insights. It computes distraction rates, habit completion, and an overall focus score, then renders a markdown report for sharing.

Modules and error handling
- `distraction.py`: totals and per-task distraction rates; skips malformed session data instead of crashing.
- `weekly_report.py`: filters sessions for a week, calculates habit completion, and exports markdown; skips bad entries and raises `ReportExportError` on export failures.
- `focuscore.py`: combines distraction and habit metrics into a weekly focus score and grade.
- `exceptions.py`: defines `ReportExportError` used by report export.

Testing and coverage (run from repo root)
```bash
$env:PYTHONPATH="."
python -m unittest -v test.test_analytics
python -m coverage run -m unittest discover -s test -t .
python -m coverage report
```
