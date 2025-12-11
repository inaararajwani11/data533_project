## Analytics subpackage overview

Transforms focus sessions and habits into weekly insights: distraction rates, habit completion, focus score/grade, and exportable reports. Defensive against malformed data and uses custom exceptions for reporting errors.

### Modules
- `distraction.py`: overall and per-task distraction rates; skips malformed session data.
- `weekly_report.py`: filters sessions for a week, computes totals, habit completion rate, and formats/exports markdown; raises `ReportExportError` on export failures.
- `focuscore.py`: combines distraction rate and habit completion into a weekly focus score and grade.
- `exceptions.py`: defines `ReportExportError`.
- `__init__.py`: package marker.

### Usage example
```python
from datetime import date
from analytics.focuscore import compute_weekly_focus_with_grade

score, grade = compute_weekly_focus_with_grade(
    sessions=[],  # List[FocusSession]
    habits=[],    # List[Habit]
    week_start=date.today(),
)
print(score, grade)
```

### Testing & coverage (repo root)
```bash
$env:PYTHONPATH="src\project"
python -m unittest -v tests.test_focuscore
python -m coverage run -m unittest discover -s tests -t .
python -m coverage report
```

### Notes
- Functions tolerate missing/partial data and clamp scores to valid ranges.
- Markdown export surfaces errors via `ReportExportError` instead of silent failure.
