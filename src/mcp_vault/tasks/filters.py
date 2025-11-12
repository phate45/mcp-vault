"""Filter implementations for task querying."""

from datetime import date
from typing import Optional
from .models import Task, PRIORITY_HIERARCHY
from .date_resolver import date_compare


class Filter:
    """Base class for all filters."""

    def matches(self, task: Task) -> bool:
        """Check if task matches this filter.

        Args:
            task: Task to check

        Returns:
            True if task matches filter, False otherwise
        """
        raise NotImplementedError


class StatusFilter(Filter):
    """Filter tasks by done/not done status."""

    def __init__(self, value: str):
        """Initialize status filter.

        Args:
            value: Either 'done' or 'not_done'
        """
        self.value = value

    def matches(self, task: Task) -> bool:
        if self.value == 'done':
            return task.is_done
        elif self.value == 'not_done':
            return not task.is_done
        return False


class DateFilter(Filter):
    """Filter tasks by date fields with operators."""

    def __init__(self, field: str, operator: str, target_date: date):
        """Initialize date filter.

        Args:
            field: Date field name ('due', 'scheduled', 'start', 'done')
            operator: Comparison operator ('before', 'after', 'on')
            target_date: Date to compare against
        """
        self.field = field
        self.operator = operator
        self.target_date = target_date

    def matches(self, task: Task) -> bool:
        # Get the appropriate date field from the task
        task_date = self._get_task_date(task)
        return date_compare(task_date, self.operator, self.target_date)

    def _get_task_date(self, task: Task) -> Optional[date]:
        """Extract the relevant date field from task."""
        field_map = {
            'due': task.due_date,
            'scheduled': task.scheduled_date,
            'start': task.start_date,
            'done': task.done_date,
        }
        return field_map.get(self.field)


class HappensFilter(Filter):
    """Filter tasks by 'happens' date (earliest of start, scheduled, due)."""

    def __init__(self, operator: str, target_date: date):
        """Initialize happens filter.

        Args:
            operator: Comparison operator ('before', 'after', 'on')
            target_date: Date to compare against
        """
        self.operator = operator
        self.target_date = target_date

    def matches(self, task: Task) -> bool:
        # Check if ANY of the three date fields matches the condition
        dates_to_check = [
            task.start_date,
            task.scheduled_date,
            task.due_date,
        ]

        for task_date in dates_to_check:
            if task_date is not None:
                if date_compare(task_date, self.operator, self.target_date):
                    return True

        return False


class PriorityFilter(Filter):
    """Filter tasks by priority level."""

    def __init__(self, comparison: str, target_priority: str):
        """Initialize priority filter.

        Args:
            comparison: Comparison type ('is', 'is_not', 'above', 'below')
            target_priority: Priority level to compare against
        """
        self.comparison = comparison
        self.target_priority = target_priority

    def matches(self, task: Task) -> bool:
        task_priority = task.priority or 'none'
        task_level = PRIORITY_HIERARCHY.get(task_priority, 3)
        target_level = PRIORITY_HIERARCHY.get(self.target_priority, 3)

        if self.comparison == 'is':
            return task_priority == self.target_priority
        elif self.comparison == 'is_not':
            return task_priority != self.target_priority
        elif self.comparison == 'above':
            # Lower number = higher priority, so "above medium" means level < medium's level
            return task_level < target_level
        elif self.comparison == 'below':
            # Higher number = lower priority, so "below medium" means level > medium's level
            return task_level > target_level

        return False


class HasFilter(Filter):
    """Filter tasks by presence/absence of date fields."""

    def __init__(self, field: str, has: bool):
        """Initialize has/no filter.

        Args:
            field: Date field name ('due', 'scheduled', 'start', 'done', 'created', 'cancelled')
            has: True for "has", False for "no"
        """
        self.field = field
        self.has = has

    def matches(self, task: Task) -> bool:
        # Get the appropriate date field from the task
        task_date = self._get_task_date(task)

        if self.has:
            return task_date is not None
        else:
            return task_date is None

    def _get_task_date(self, task: Task) -> Optional[date]:
        """Extract the relevant date field from task."""
        field_map = {
            'due': task.due_date,
            'scheduled': task.scheduled_date,
            'start': task.start_date,
            'done': task.done_date,
            # Note: 'created' and 'cancelled' not in MVP but here for completeness
            'created': None,
            'cancelled': None,
        }
        return field_map.get(self.field)


class AndFilter(Filter):
    """Combine multiple filters with AND logic."""

    def __init__(self, filters: list[Filter]):
        """Initialize AND filter.

        Args:
            filters: List of filters to combine
        """
        self.filters = filters

    def matches(self, task: Task) -> bool:
        # All filters must match
        return all(f.matches(task) for f in self.filters)


class OrFilter(Filter):
    """Combine multiple filters with OR logic."""

    def __init__(self, filters: list[Filter]):
        """Initialize OR filter.

        Args:
            filters: List of filters to combine
        """
        self.filters = filters

    def matches(self, task: Task) -> bool:
        # At least one filter must match
        return any(f.matches(task) for f in self.filters)


class NotFilter(Filter):
    """Negate a filter."""

    def __init__(self, filter: Filter):
        """Initialize NOT filter.

        Args:
            filter: Filter to negate
        """
        self.filter = filter

    def matches(self, task: Task) -> bool:
        return not self.filter.matches(task)
