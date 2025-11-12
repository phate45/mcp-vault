"""Query parsing - convert query statements into filter objects."""

import re
from typing import Optional
from .models import Query
from .filters import (
    Filter,
    StatusFilter,
    DateFilter,
    HappensFilter,
    PriorityFilter,
    HasFilter,
    AndFilter,
    OrFilter,
)
from .date_resolver import resolve_date


# Regex patterns for filter recognition
STATUS_DONE_PATTERN = re.compile(r'^done$', re.IGNORECASE)
STATUS_NOT_DONE_PATTERN = re.compile(r'^not done$', re.IGNORECASE)

DATE_FILTER_PATTERN = re.compile(
    r'^(due|scheduled|start|done)\s+(before|after|on)\s+(.+)$',
    re.IGNORECASE
)

HAPPENS_FILTER_PATTERN = re.compile(
    r'^happens\s+(before|after|on)\s+(.+)$',
    re.IGNORECASE
)

HAS_FILTER_PATTERN = re.compile(
    r'^(has|no)\s+(due|scheduled|start|created|done|cancelled)\s+date$',
    re.IGNORECASE
)

PRIORITY_FILTER_PATTERN = re.compile(
    r'^priority\s+is\s+(.+)$',
    re.IGNORECASE
)

# Boolean expression pattern (simplified for MVP)
BOOLEAN_EXPR_PATTERN = re.compile(
    r'^\((.+)\)\s+(AND|OR)\s+\((.+)\)$',
    re.IGNORECASE
)


def parse_query(query_source: str) -> Query:
    """Parse a query source string into a Query object.

    Args:
        query_source: Multi-line query string

    Returns:
        Query object with parsed filters or error
    """
    lines = query_source.strip().split('\n')
    filters = []
    errors = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        filter_obj = parse_line(line)
        if filter_obj is not None:
            filters.append(filter_obj)
        else:
            errors.append(f"Could not parse line: {line}")

    if errors:
        return Query(filters=[], error="; ".join(errors))

    return Query(filters=filters)


def parse_line(line: str) -> Optional[Filter]:
    """Parse a single query line into a Filter object.

    Args:
        line: A single query statement line

    Returns:
        Filter object if line is valid, None otherwise
    """
    line = line.strip()

    # Try status filters first
    if STATUS_DONE_PATTERN.match(line):
        return StatusFilter('done')

    if STATUS_NOT_DONE_PATTERN.match(line):
        return StatusFilter('not_done')

    # Try date filters
    match = DATE_FILTER_PATTERN.match(line)
    if match:
        field = match.group(1).lower()
        operator = match.group(2).lower()
        date_str = match.group(3)

        target_date = resolve_date(date_str)
        if target_date is None:
            return None

        return DateFilter(field, operator, target_date)

    # Try happens filter
    match = HAPPENS_FILTER_PATTERN.match(line)
    if match:
        operator = match.group(1).lower()
        date_str = match.group(2)

        target_date = resolve_date(date_str)
        if target_date is None:
            return None

        return HappensFilter(operator, target_date)

    # Try has/no filter
    match = HAS_FILTER_PATTERN.match(line)
    if match:
        has_or_no = match.group(1).lower()
        field = match.group(2).lower()

        has = (has_or_no == 'has')
        return HasFilter(field, has)

    # Try priority filter
    match = PRIORITY_FILTER_PATTERN.match(line)
    if match:
        priority_clause = match.group(1).lower().strip()
        return parse_priority_clause(priority_clause)

    # Try boolean expression (AND/OR)
    match = BOOLEAN_EXPR_PATTERN.match(line)
    if match:
        left_expr = match.group(1).strip()
        operator = match.group(2).upper()
        right_expr = match.group(3).strip()

        left_filter = parse_line(left_expr)
        right_filter = parse_line(right_expr)

        if left_filter is None or right_filter is None:
            return None

        if operator == 'AND':
            return AndFilter([left_filter, right_filter])
        elif operator == 'OR':
            return OrFilter([left_filter, right_filter])

    # Could not parse
    return None


def parse_priority_clause(clause: str) -> Optional[Filter]:
    """Parse a priority clause into a PriorityFilter.

    Args:
        clause: The text after "priority is", e.g., "high", "above none", "not high"

    Returns:
        PriorityFilter object, or None if invalid
    """
    # Direct priority match: "priority is highest"
    if clause in ['highest', 'high', 'medium', 'low', 'lowest', 'none']:
        return PriorityFilter('is', clause)

    # "priority is not X"
    if clause.startswith('not '):
        priority = clause[4:].strip()
        if priority in ['highest', 'high', 'medium', 'low', 'lowest', 'none']:
            return PriorityFilter('is_not', priority)

    # "priority is above X"
    if clause.startswith('above '):
        priority = clause[6:].strip()
        if priority in ['highest', 'high', 'medium', 'low', 'lowest', 'none']:
            return PriorityFilter('above', priority)

    # "priority is below X"
    if clause.startswith('below '):
        priority = clause[6:].strip()
        if priority in ['highest', 'high', 'medium', 'low', 'lowest', 'none']:
            return PriorityFilter('below', priority)

    return None
