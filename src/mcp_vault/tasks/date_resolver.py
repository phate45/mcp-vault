"""Date resolution with hardcoded relative date mappings."""

from datetime import date, timedelta
from typing import Optional


# Hardcoded relative date mappings for MVP
# Keys are lowercase for case-insensitive matching
RELATIVE_DATE_MAP = {
    'today': lambda ref: ref,
    'tomorrow': lambda ref: ref + timedelta(days=1),
    'yesterday': lambda ref: ref - timedelta(days=1),
    'in one week': lambda ref: ref + timedelta(days=7),
    'in two weeks': lambda ref: ref + timedelta(days=14),
}


def resolve_date(date_str: str, reference_date: Optional[date] = None) -> Optional[date]:
    """Resolve a date string to an actual date.

    Args:
        date_str: Date string (relative like "today" or absolute like "2025-11-12")
        reference_date: Reference date for relative calculations (defaults to today)

    Returns:
        Resolved date object, or None if invalid
    """
    if reference_date is None:
        reference_date = date.today()

    # Normalize the date string for case-insensitive matching
    date_str_lower = date_str.strip().lower()

    # Try relative date mapping first
    if date_str_lower in RELATIVE_DATE_MAP:
        return RELATIVE_DATE_MAP[date_str_lower](reference_date)

    # Try absolute date parsing (YYYY-MM-DD)
    try:
        year, month, day = date_str.strip().split('-')
        return date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return None


def date_compare(task_date: Optional[date], operator: str, target_date: date) -> bool:
    """Compare a task date with a target date using the specified operator.

    Args:
        task_date: The date from the task (may be None)
        operator: Comparison operator ('before', 'after', 'on')
        target_date: The date to compare against

    Returns:
        True if comparison matches, False otherwise
    """
    if task_date is None:
        return False

    operator_lower = operator.lower()

    if operator_lower == 'before':
        return task_date < target_date
    elif operator_lower == 'after':
        return task_date > target_date
    elif operator_lower == 'on':
        return task_date == target_date
    else:
        # Unknown operator
        return False
