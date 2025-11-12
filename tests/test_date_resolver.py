"""Unit tests for date resolution."""

from datetime import date, timedelta
from mcp_vault.tasks.date_resolver import resolve_date, date_compare


def test_resolve_today():
    """Test resolving 'today'."""
    ref_date = date(2025, 11, 12)
    result = resolve_date("today", ref_date)
    assert result == date(2025, 11, 12)


def test_resolve_tomorrow():
    """Test resolving 'tomorrow'."""
    ref_date = date(2025, 11, 12)
    result = resolve_date("tomorrow", ref_date)
    assert result == date(2025, 11, 13)


def test_resolve_yesterday():
    """Test resolving 'yesterday'."""
    ref_date = date(2025, 11, 12)
    result = resolve_date("yesterday", ref_date)
    assert result == date(2025, 11, 11)


def test_resolve_in_one_week():
    """Test resolving 'in one week'."""
    ref_date = date(2025, 11, 12)
    result = resolve_date("in one week", ref_date)
    assert result == date(2025, 11, 19)


def test_resolve_in_two_weeks():
    """Test resolving 'in two weeks'."""
    ref_date = date(2025, 11, 12)
    result = resolve_date("in two weeks", ref_date)
    assert result == date(2025, 11, 26)


def test_resolve_case_insensitive():
    """Test that date resolution is case-insensitive."""
    ref_date = date(2025, 11, 12)

    assert resolve_date("TODAY", ref_date) == date(2025, 11, 12)
    assert resolve_date("Tomorrow", ref_date) == date(2025, 11, 13)
    assert resolve_date("YESTERDAY", ref_date) == date(2025, 11, 11)
    assert resolve_date("In One Week", ref_date) == date(2025, 11, 19)


def test_resolve_absolute_date():
    """Test resolving absolute date strings."""
    result = resolve_date("2025-11-15")
    assert result == date(2025, 11, 15)

    result = resolve_date("2025-12-25")
    assert result == date(2025, 12, 25)


def test_resolve_invalid_date():
    """Test resolving invalid date strings."""
    result = resolve_date("invalid date")
    assert result is None

    result = resolve_date("2025-13-45")  # Invalid date
    assert result is None


def test_date_compare_before():
    """Test date comparison with 'before' operator."""
    task_date = date(2025, 11, 10)
    target_date = date(2025, 11, 12)

    assert date_compare(task_date, "before", target_date) is True
    assert date_compare(target_date, "before", task_date) is False
    assert date_compare(task_date, "before", task_date) is False


def test_date_compare_after():
    """Test date comparison with 'after' operator."""
    task_date = date(2025, 11, 14)
    target_date = date(2025, 11, 12)

    assert date_compare(task_date, "after", target_date) is True
    assert date_compare(target_date, "after", task_date) is False
    assert date_compare(task_date, "after", task_date) is False


def test_date_compare_on():
    """Test date comparison with 'on' operator."""
    task_date = date(2025, 11, 12)
    target_date = date(2025, 11, 12)

    assert date_compare(task_date, "on", target_date) is True
    assert date_compare(task_date, "on", date(2025, 11, 13)) is False


def test_date_compare_with_none():
    """Test date comparison when task date is None."""
    assert date_compare(None, "before", date(2025, 11, 12)) is False
    assert date_compare(None, "after", date(2025, 11, 12)) is False
    assert date_compare(None, "on", date(2025, 11, 12)) is False


def test_date_compare_case_insensitive():
    """Test that operator comparison is case-insensitive."""
    task_date = date(2025, 11, 10)
    target_date = date(2025, 11, 12)

    assert date_compare(task_date, "BEFORE", target_date) is True
    assert date_compare(task_date, "Before", target_date) is True
    assert date_compare(date(2025, 11, 14), "AFTER", target_date) is True


