"""Unit tests for filter implementations."""

from datetime import date
from mcp_vault.tasks.models import Task
from mcp_vault.tasks.filters import (
    StatusFilter,
    DateFilter,
    HappensFilter,
    PriorityFilter,
    HasFilter,
    AndFilter,
    OrFilter,
    NotFilter,
)


# Helper function to create test tasks
def create_task(status=' ', description='Test', priority=None, due_date=None,
                scheduled_date=None, start_date=None, done_date=None, created_date=None):
    """Create a test task with specified fields."""
    return Task(
        status=status,
        description=description,
        priority=priority,
        start_date=start_date,
        scheduled_date=scheduled_date,
        due_date=due_date,
        done_date=done_date,
        created_date=created_date,
        source_line=f"- [{status}] {description}",
        file_path="test.md",
        line_number=1
    )


def test_status_filter_done():
    """Test StatusFilter for done tasks."""
    filter_obj = StatusFilter('done')

    done_task = create_task(status='x')
    not_done_task = create_task(status=' ')

    assert filter_obj.matches(done_task) is True
    assert filter_obj.matches(not_done_task) is False


def test_status_filter_not_done():
    """Test StatusFilter for not done tasks."""
    filter_obj = StatusFilter('not_done')

    done_task = create_task(status='x')
    not_done_task = create_task(status=' ')

    assert filter_obj.matches(done_task) is False
    assert filter_obj.matches(not_done_task) is True


def test_date_filter_due_before():
    """Test DateFilter with due date before."""
    filter_obj = DateFilter('due', 'before', date(2025, 11, 15))

    task_before = create_task(due_date=date(2025, 11, 10))
    task_after = create_task(due_date=date(2025, 11, 20))
    task_no_date = create_task(due_date=None)

    assert filter_obj.matches(task_before) is True
    assert filter_obj.matches(task_after) is False
    assert filter_obj.matches(task_no_date) is False


def test_date_filter_due_after():
    """Test DateFilter with due date after."""
    filter_obj = DateFilter('due', 'after', date(2025, 11, 15))

    task_before = create_task(due_date=date(2025, 11, 10))
    task_after = create_task(due_date=date(2025, 11, 20))

    assert filter_obj.matches(task_before) is False
    assert filter_obj.matches(task_after) is True


def test_date_filter_due_on():
    """Test DateFilter with due date on."""
    filter_obj = DateFilter('due', 'on', date(2025, 11, 15))

    task_same = create_task(due_date=date(2025, 11, 15))
    task_different = create_task(due_date=date(2025, 11, 16))

    assert filter_obj.matches(task_same) is True
    assert filter_obj.matches(task_different) is False


def test_date_filter_scheduled():
    """Test DateFilter with scheduled field."""
    filter_obj = DateFilter('scheduled', 'before', date(2025, 11, 15))

    task = create_task(scheduled_date=date(2025, 11, 10))
    assert filter_obj.matches(task) is True


def test_date_filter_start():
    """Test DateFilter with start field."""
    filter_obj = DateFilter('start', 'after', date(2025, 11, 15))

    task = create_task(start_date=date(2025, 11, 20))
    assert filter_obj.matches(task) is True


def test_happens_filter():
    """Test HappensFilter checks any of start/scheduled/due."""
    filter_obj = HappensFilter('before', date(2025, 11, 15))

    # Task with only due date matching
    task_due = create_task(due_date=date(2025, 11, 10))
    assert filter_obj.matches(task_due) is True

    # Task with only scheduled date matching
    task_scheduled = create_task(scheduled_date=date(2025, 11, 12))
    assert filter_obj.matches(task_scheduled) is True

    # Task with only start date matching
    task_start = create_task(start_date=date(2025, 11, 13))
    assert filter_obj.matches(task_start) is True

    # Task with no dates
    task_no_dates = create_task()
    assert filter_obj.matches(task_no_dates) is False

    # Task with dates all after target
    task_all_after = create_task(
        start_date=date(2025, 11, 16),
        scheduled_date=date(2025, 11, 17),
        due_date=date(2025, 11, 18)
    )
    assert filter_obj.matches(task_all_after) is False


def test_priority_filter_is():
    """Test PriorityFilter with 'is' comparison."""
    filter_high = PriorityFilter('is', 'high')

    task_high = create_task(priority='high')
    task_medium = create_task(priority='medium')
    task_none = create_task(priority=None)

    assert filter_high.matches(task_high) is True
    assert filter_high.matches(task_medium) is False
    assert filter_high.matches(task_none) is False


def test_priority_filter_is_not():
    """Test PriorityFilter with 'is_not' comparison."""
    filter_obj = PriorityFilter('is_not', 'high')

    task_high = create_task(priority='high')
    task_medium = create_task(priority='medium')

    assert filter_obj.matches(task_high) is False
    assert filter_obj.matches(task_medium) is True


def test_priority_filter_above():
    """Test PriorityFilter with 'above' comparison."""
    filter_obj = PriorityFilter('above', 'medium')

    # Above medium = highest, high
    task_highest = create_task(priority='highest')
    task_high = create_task(priority='high')
    task_medium = create_task(priority='medium')
    task_low = create_task(priority='low')

    assert filter_obj.matches(task_highest) is True
    assert filter_obj.matches(task_high) is True
    assert filter_obj.matches(task_medium) is False
    assert filter_obj.matches(task_low) is False


def test_priority_filter_below():
    """Test PriorityFilter with 'below' comparison."""
    filter_obj = PriorityFilter('below', 'medium')

    # Below medium = none, low, lowest
    task_high = create_task(priority='high')
    task_medium = create_task(priority='medium')
    task_none = create_task(priority=None)
    task_low = create_task(priority='low')
    task_lowest = create_task(priority='lowest')

    assert filter_obj.matches(task_high) is False
    assert filter_obj.matches(task_medium) is False
    assert filter_obj.matches(task_none) is True
    assert filter_obj.matches(task_low) is True
    assert filter_obj.matches(task_lowest) is True


def test_has_filter_has_due():
    """Test HasFilter for presence of due date."""
    filter_obj = HasFilter('due', True)

    task_with_due = create_task(due_date=date(2025, 11, 15))
    task_without_due = create_task(due_date=None)

    assert filter_obj.matches(task_with_due) is True
    assert filter_obj.matches(task_without_due) is False


def test_has_filter_no_due():
    """Test HasFilter for absence of due date."""
    filter_obj = HasFilter('due', False)

    task_with_due = create_task(due_date=date(2025, 11, 15))
    task_without_due = create_task(due_date=None)

    assert filter_obj.matches(task_with_due) is False
    assert filter_obj.matches(task_without_due) is True


def test_and_filter():
    """Test AndFilter combines filters with AND logic."""
    filter1 = StatusFilter('not_done')
    filter2 = PriorityFilter('is', 'high')
    and_filter = AndFilter([filter1, filter2])

    # Both conditions met
    task_match = create_task(status=' ', priority='high')
    assert and_filter.matches(task_match) is True

    # Only first condition met
    task_partial = create_task(status=' ', priority='low')
    assert and_filter.matches(task_partial) is False

    # Only second condition met
    task_partial2 = create_task(status='x', priority='high')
    assert and_filter.matches(task_partial2) is False


def test_or_filter():
    """Test OrFilter combines filters with OR logic."""
    filter1 = PriorityFilter('is', 'high')
    filter2 = PriorityFilter('is', 'highest')
    or_filter = OrFilter([filter1, filter2])

    # First condition met
    task1 = create_task(priority='high')
    assert or_filter.matches(task1) is True

    # Second condition met
    task2 = create_task(priority='highest')
    assert or_filter.matches(task2) is True

    # Neither condition met
    task3 = create_task(priority='low')
    assert or_filter.matches(task3) is False


def test_not_filter():
    """Test NotFilter negates a filter."""
    status_filter = StatusFilter('done')
    not_filter = NotFilter(status_filter)

    done_task = create_task(status='x')
    not_done_task = create_task(status=' ')

    # NOT done = not done
    assert not_filter.matches(done_task) is False
    assert not_filter.matches(not_done_task) is True


