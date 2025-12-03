"""
weekly_report.py

Generate a weekly productivity summary using FocusSession + Habit data.

Responsibilities
----------------
- Filter sessions for the selected week
- Compute weekly metrics
- Format report text / markdown
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from core.focus_session import FocusSession
from core.habit import Habit


def filter_sessions_for_week(
    sessions: List[FocusSession],
    week_start: date,
) -> List[FocusSession]:
    """
    Return all sessions whose start_time falls within the
    7‑day week starting at week_start (inclusive).
    """
    week_end_exclusive = week_start + timedelta(days=7)

    result: List[FocusSession] = []
    for s in sessions:
        start_day = s.start_time.date()
        if week_start <= start_day < week_end_exclusive:
            result.append(s)
    return result


def _habit_completion_rate_for_week(
    habits: List[Habit],
    week_start: date,
) -> float:
    """
    Very simple habit adherence metric:
    fraction of habits that were completed at least once
    during the given week.
    """
    if not habits:
        return 0.0

    week_end_inclusive = week_start + timedelta(days=6)
    completed = 0

    for h in habits:
        last = h.last_completed
        if last is not None and week_start <= last <= week_end_inclusive:
            completed += 1

    return completed / len(habits)


def compute_weekly_summary(
    sessions: List[FocusSession],
    habits: List[Habit],
    week_start: date,
) -> Dict[str, Any]:
    """
    Compute raw weekly metrics.

    Returns a dict containing e.g.:
      - week_start / week_end
      - total_focus_minutes
      - num_sessions
      - average_session_length
      - total_distractions
      - habit_completion_rate
      - top_habits (by streak)
    """
    week_sessions = filter_sessions_for_week(sessions, week_start)

    total_focus_minutes = 0
    total_distractions = 0

    for s in week_sessions:
        duration = s.duration_minutes()
        if duration is not None:
            total_focus_minutes += duration
        total_distractions += s.distractions

    num_sessions = len(week_sessions)
    if num_sessions > 0:
        average_session_length = total_focus_minutes / num_sessions
    else:
        average_session_length = 0.0

    habit_completion_rate = _habit_completion_rate_for_week(habits, week_start)

    # Top habits by streak (simple heuristic)
    sorted_habits = sorted(
        habits,
        key=lambda h: getattr(h, "streak", 0),
        reverse=True,
    )
    top_habits = [h.name for h in sorted_habits[:3]]

    summary: Dict[str, Any] = {
        "week_start": week_start,
        "week_end": week_start + timedelta(days=6),
        "total_focus_minutes": total_focus_minutes,
        "num_sessions": num_sessions,
        "average_session_length": average_session_length,
        "total_distractions": total_distractions,
        "habit_completion_rate": habit_completion_rate,
        "top_habits": top_habits,
    }

    return summary


def format_weekly_report_text(summary: Dict[str, Any]) -> str:
    """
    Turn the summary dict into a multi‑line string suitable
    for CLI output or markdown.
    """
    week_start = summary.get("week_start")
    week_end = summary.get("week_end")

    lines = [
        f"Weekly Report ({week_start} -> {week_end})",
        "-" * 40,
        f"Total focus minutes   : {summary.get('total_focus_minutes', 0)}",
        f"Number of sessions    : {summary.get('num_sessions', 0)}",
        f"Avg session length    : {summary.get('average_session_length', 0):.1f} min",
        f"Total distractions    : {summary.get('total_distractions', 0)}",
        f"Habit completion rate : {summary.get('habit_completion_rate', 0.0) * 100:.1f} %",
        "",
        "Top habits (by streak):",
    ]

    top_habits = summary.get("top_habits", []) or []
    if not top_habits:
        lines.append("  (no habits tracked)")
    else:
        for name in top_habits:
            lines.append(f"  - {name}")

    return "\n".join(lines)


def export_weekly_report_markdown(
    summary: Dict[str, Any],
    filename: str,
) -> None:
    """
    Save the formatted weekly report as a .md file.
    """
    text = format_weekly_report_text(summary)
    with open(filename, "w", encoding="utf-8") as f:
        # Simple markdown wrapper
        f.write("# Weekly Focus Report\n\n")
        f.write("```\n")
        f.write(text)
        f.write("\n```\n")
