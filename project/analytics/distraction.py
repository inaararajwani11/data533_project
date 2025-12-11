from __future__ import annotations

from datetime import date
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.focus_session import FocusSession
from analytics.focus_errors import EmptyDataError, InvalidSessionError, FocusAnalyticsError


def total_distractions(sessions: List[FocusSession]) -> int:
    """Calculate total distractions with error handling."""
    try:
        if not isinstance(sessions, list):
            raise TypeError("sessions must be a list")
            
        if not sessions:
            return 0

        total = 0
        for i, s in enumerate(sessions):
            if not isinstance(s, FocusSession):
                raise InvalidSessionError(f"Session at index {i} is not a FocusSession object")
                
            if s.distractions is None:
                continue  # Skip sessions with no distraction data
                
            if s.distractions < 0:
                raise InvalidSessionError(f"Session at index {i} has negative distractions: {s.distractions}")
                
            total += s.distractions

        return total
        
    except (TypeError, InvalidSessionError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error calculating total distractions: {str(e)}") from e


def distraction_rate_per_hour(
    sessions: List[FocusSession],
) -> Optional[float]:
    """Calculate distraction rate per hour with error handling."""
    try:
        if not isinstance(sessions, list):
            raise TypeError("sessions must be a list")
            
        if not sessions:
            return None

        total_minutes = 0
        total_distractions_count = 0
        valid_sessions = 0

        for i, s in enumerate(sessions):
            if not isinstance(s, FocusSession):
                raise InvalidSessionError(f"Session at index {i} is not a FocusSession object")
                
            try:
                duration = s.duration_minutes()
                if duration is not None and duration > 0:
                    if s.distractions is None:
                        continue  # Skip sessions with no distraction data
                        
                    if s.distractions < 0:
                        raise InvalidSessionError(f"Session at index {i} has negative distractions: {s.distractions}")
                        
                    total_minutes += duration
                    total_distractions_count += s.distractions
                    valid_sessions += 1
                    
            except InvalidSessionError:
                raise
            except Exception as e:
                raise FocusAnalyticsError(f"Error processing session at index {i}: {str(e)}") from e

        if total_minutes == 0 or valid_sessions == 0:
            return None

        hours = total_minutes / 60.0
        return total_distractions_count / hours
        
    except (TypeError, InvalidSessionError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error calculating distraction rate per hour: {str(e)}") from e


def distractions_by_day(
    sessions: List[FocusSession],
) -> Dict[date, int]:
    """Calculate distractions by day with error handling."""
    try:
        if not isinstance(sessions, list):
            raise TypeError("sessions must be a list")
            
        result: Dict[date, int] = {}

        for i, s in enumerate(sessions):
            if not isinstance(s, FocusSession):
                raise InvalidSessionError(f"Session at index {i} is not a FocusSession object")
                
            if s.start_time is None:
                raise InvalidSessionError(f"Session at index {i} has no start_time")
                
            if s.distractions is None:
                continue  # Skip sessions with no distraction data
                
            if s.distractions < 0:
                raise InvalidSessionError(f"Session at index {i} has negative distractions: {s.distractions}")
                
            day = s.start_time.date()
            result[day] = result.get(day, 0) + s.distractions

        return result
        
    except (TypeError, InvalidSessionError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error calculating distractions by day: {str(e)}") from e


def distraction_rate_by_task(
    sessions: List[FocusSession],
) -> Dict[str, float]:
    """Calculate distraction rate by task with error handling."""
    try:
        if not isinstance(sessions, list):
            raise TypeError("sessions must be a list")
            
        total_minutes_by_label: Dict[str, int] = {}
        total_distractions_by_label: Dict[str, int] = {}
        valid_sessions_count = 0

        for i, s in enumerate(sessions):
            if not isinstance(s, FocusSession):
                raise InvalidSessionError(f"Session at index {i} is not a FocusSession object")
                
            try:
                # Derive a label with error handling
                label = "Unknown"
                try:
                    if getattr(s, "task", None) is not None:
                        label = getattr(s.task, "name", "Task")
                    elif getattr(s, "habit", None) is not None:
                        label = f"Habit: {getattr(s.habit, 'name', 'Habit')}"
                    else:
                        label = s.label or "Unknown"
                except (AttributeError, TypeError):
                    label = "Unknown"

                duration = s.duration_minutes()
                if duration is None or duration <= 0:
                    continue

                if s.distractions is None:
                    continue  # Skip sessions with no distraction data
                    
                if s.distractions < 0:
                    raise InvalidSessionError(f"Session at index {i} has negative distractions: {s.distractions}")

                total_minutes_by_label[label] = total_minutes_by_label.get(label, 0) + duration
                total_distractions_by_label[label] = (
                    total_distractions_by_label.get(label, 0) + s.distractions
                )
                valid_sessions_count += 1
                
            except InvalidSessionError:
                raise
            except Exception as e:
                raise FocusAnalyticsError(f"Error processing session at index {i}: {str(e)}") from e

        if valid_sessions_count == 0:
            return {}

        rates: Dict[str, float] = {}
        for label, minutes in total_minutes_by_label.items():
            hours = minutes / 60.0
            if hours <= 0:
                continue
            total = total_distractions_by_label.get(label, 0)
            rates[label] = total / hours

        return rates
        
    except (TypeError, InvalidSessionError):
        raise
    except Exception as e:
        raise FocusAnalyticsError(f"Error calculating distraction rate by task: {str(e)}") from e