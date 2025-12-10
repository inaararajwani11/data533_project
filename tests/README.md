The test subpackage verifies the core models and planner flows with `unittest`.

- `test_core.py`: tasks, habits, focus sessions (creation, listing, distractions, ratings, durations).
- `test_focuscore.py`: focus score/grade and weekly metrics with mocks.
- `test_planner.py`: end-to-end planner behavior (modes, validation, pomodoro split, recovery interleave, deadlines, energy clamping).
- `test_planner_helpers.py`: helper utilities and edge cases (parse/normalize, pomodoro cutoff when out of time, recovery tail appends).

Run planner tests only:
```bash
python -m unittest -v tests.test_planner tests.test_planner_helpers
```

Run full suite with coverage (PowerShell from repo root):
```bash
$env:PYTHONPATH="src\project"
python -m coverage run -m unittest discover -s tests -t .
python -m coverage report
```
