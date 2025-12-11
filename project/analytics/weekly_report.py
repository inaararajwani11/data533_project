from __future__ import annotations

from datetime import date, timedelta
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Allow running this module directly (python weekly_report.py) by adding repo root to sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.focus_session import FocusSession
from core.habit import Habit
from analytics.focus_errors import InvalidDateError, EmptyDataError, InvalidSessionError, FileExportError


def filter_sessions_for_week(
    sessions: List[FocusSession],
    week_start: date,
) -> List[FocusSession]:
    """Filter focus sessions for a specific week with error handling."""
    try:
        if not isinstance(week_start, date):
            raise InvalidDateError(f"week_start must be a date object, got {type(week_start)}")
        
        if not isinstance(sessions, list):
            raise TypeError("sessions must be a list")
        
        week_end_exclusive = week_start + timedelta(days=7)

        result: List[FocusSession] = []
        for i, s in enumerate(sessions):
            if not isinstance(s, FocusSession):
                raise InvalidSessionError(f"Session at index {i} is not a FocusSession object")
            
            if s.start_time is None:
                raise InvalidSessionError(f"Session at index {i} has no start_time")
                
            start_day = s.start_time.date()
            if week_start <= start_day < week_end_exclusive:
                result.append(s)
        return result
        
    except InvalidDateError:
        raise
    except InvalidSessionError:
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error filtering sessions: {str(e)}") from e


def _habit_completion_rate_for_week(
    habits: List[Habit],
    week_start: date,
) -> float:
    """Calculate habit completion rate for a week with error handling."""
    try:
        if not isinstance(week_start, date):
            raise InvalidDateError(f"week_start must be a date object, got {type(week_start)}")
        
        if not isinstance(habits, list):
            raise TypeError("habits must be a list")

        if not habits:
            return 0.0

        week_end_inclusive = week_start + timedelta(days=6)
        completed = 0

        for i, h in enumerate(habits):
            if not isinstance(h, Habit):
                raise TypeError(f"Habit at index {i} is not a Habit object")
                
            last = h.last_completed
            if last is not None and week_start <= last <= week_end_inclusive:
                completed += 1

        return completed / len(habits)
        
    except InvalidDateError:
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error calculating habit completion rate: {str(e)}") from e


def compute_weekly_summary(
    sessions: List[FocusSession],
    habits: List[Habit],
    week_start: date,
) -> Dict[str, Any]:
    """Compute weekly summary with comprehensive error handling."""
    try:
        if not isinstance(week_start, date):
            raise InvalidDateError(f"week_start must be a date object, got {type(week_start)}")
        
        if not isinstance(sessions, list):
            raise TypeError("sessions must be a list")
            
        if not isinstance(habits, list):
            raise TypeError("habits must be a list")

        week_sessions = filter_sessions_for_week(sessions, week_start)

        total_focus_minutes = 0
        total_distractions = 0
        valid_sessions = 0

        for i, s in enumerate(week_sessions):
            try:
                if not isinstance(s, FocusSession):
                    raise InvalidSessionError(f"Invalid session at index {i}")
                    
                duration = s.duration_minutes()
                if duration is not None:
                    if duration < 0:
                        raise InvalidSessionError(f"Session at index {i} has negative duration: {duration}")
                    total_focus_minutes += duration
                    valid_sessions += 1
                    
                if s.distractions is not None and s.distractions >= 0:
                    total_distractions += s.distractions
                else:
                    # Skip invalid distraction counts but don't fail the whole process
                    continue
                    
            except InvalidSessionError:
                raise
            except Exception as e:
                raise FocusAnalyticsError(f"Error processing session at index {i}: {str(e)}") from e

        num_sessions = len(week_sessions)
        if valid_sessions > 0:
            average_session_length = total_focus_minutes / valid_sessions
        else:
            average_session_length = 0.0

        habit_completion_rate = _habit_completion_rate_for_week(habits, week_start)

        # Top habits by streak (simple heuristic)
        try:
            sorted_habits = sorted(
                habits,
                key=lambda h: getattr(h, "streak", 0),
                reverse=True,
            )
            top_habits = [h.name for h in sorted_habits[:3] if hasattr(h, 'name') and h.name]
        except Exception as e:
            # If sorting fails, use empty list but don't fail the whole function
            top_habits = []

        summary: Dict[str, Any] = {
            "week_start": week_start,
            "week_end": week_start + timedelta(days=6),
            "total_focus_minutes": total_focus_minutes,
            "num_sessions": num_sessions,
            "valid_sessions": valid_sessions,
            "average_session_length": average_session_length,
            "total_distractions": total_distractions,
            "habit_completion_rate": habit_completion_rate,
            "top_habits": top_habits,
        }

        return summary
        
    except (InvalidDateError, InvalidSessionError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error computing weekly summary: {str(e)}") from e


def format_weekly_report_text(summary: Dict[str, Any]) -> str:
    """Format weekly report as text with error handling."""
    try:
        if not isinstance(summary, dict):
            raise TypeError("summary must be a dictionary")
            
        week_start = summary.get("week_start")
        week_end = summary.get("week_end")

        if not isinstance(week_start, date) or not isinstance(week_end, date):
            raise InvalidDateError("week_start and week_end must be date objects")

        lines = [
            f"Weekly Report ({week_start} -> {week_end})",
            "-" * 40,
            f"Total focus minutes   : {summary.get('total_focus_minutes', 0)}",
            f"Number of sessions    : {summary.get('num_sessions', 0)}",
            f"Valid sessions        : {summary.get('valid_sessions', 0)}",
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
                if not isinstance(name, str):
                    raise TypeError("Habit name must be a string")
                lines.append(f"  - {name}")

        return "\n".join(lines)
        
    except (InvalidDateError, TypeError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error formatting weekly report: {str(e)}") from e


def export_weekly_report_markdown(
    summary: Dict[str, Any],
    filename: str,
) -> None:
    """Export weekly report to markdown file with error handling."""
    try:
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")
            
        if not filename:
            raise ValueError("filename cannot be empty")

        text = format_weekly_report_text(summary)
        
        try:
            path = Path(filename)
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                # Simple markdown wrapper
                f.write("# Weekly Focus Report\n\n")
                f.write("```\n")
                f.write(text)
                f.write("\n```\n")
                
        except IOError as e:
            raise FileExportError(f"Failed to write to file {filename}: {str(e)}") from e
        except PermissionError as e:
            raise FileExportError(f"Permission denied for file {filename}: {str(e)}") from e
            
    except (FileExportError, TypeError, ValueError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error exporting weekly report: {str(e)}") from e