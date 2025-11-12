"""Unit tests for query parsing."""

from datetime import date
from mcp_vault.tasks.query_parser import parse_query, parse_line
from mcp_vault.tasks.filters import (
    StatusFilter,
    DateFilter,
    HappensFilter,
    PriorityFilter,
    HasFilter,
    AndFilter,
)


def test_parse_done():
    """Test parsing 'done' query."""
    filter_obj = parse_line("done")
    assert isinstance(filter_obj, StatusFilter)
    assert filter_obj.value == 'done'


def test_parse_not_done():
    """Test parsing 'not done' query."""
    filter_obj = parse_line("not done")
    assert isinstance(filter_obj, StatusFilter)
    assert filter_obj.value == 'not_done'


def test_parse_due_before():
    """Test parsing 'due before' query."""
    filter_obj = parse_line("due before 2025-11-15")
    assert isinstance(filter_obj, DateFilter)
    assert filter_obj.field == 'due'
    assert filter_obj.operator == 'before'
    assert filter_obj.target_date == date(2025, 11, 15)


def test_parse_due_after():
    """Test parsing 'due after' query."""
    filter_obj = parse_line("due after tomorrow")
    assert isinstance(filter_obj, DateFilter)
    assert filter_obj.field == 'due'
    assert filter_obj.operator == 'after'
    # tomorrow will be resolved relative to current date


def test_parse_scheduled_on():
    """Test parsing 'scheduled on' query."""
    filter_obj = parse_line("scheduled on today")
    assert isinstance(filter_obj, DateFilter)
    assert filter_obj.field == 'scheduled'
    assert filter_obj.operator == 'on'


def test_parse_happens_before():
    """Test parsing 'happens before' query."""
    filter_obj = parse_line("happens before today")
    assert isinstance(filter_obj, HappensFilter)
    assert filter_obj.operator == 'before'


def test_parse_happens_today():
    """Test parsing 'happens today' (happens on today)."""
    filter_obj = parse_line("happens on today")
    assert isinstance(filter_obj, HappensFilter)
    assert filter_obj.operator == 'on'


def test_parse_has_due_date():
    """Test parsing 'has due date' query."""
    filter_obj = parse_line("has due date")
    assert isinstance(filter_obj, HasFilter)
    assert filter_obj.field == 'due'
    assert filter_obj.has is True


def test_parse_no_scheduled_date():
    """Test parsing 'no scheduled date' query."""
    filter_obj = parse_line("no scheduled date")
    assert isinstance(filter_obj, HasFilter)
    assert filter_obj.field == 'scheduled'
    assert filter_obj.has is False


def test_parse_priority_is():
    """Test parsing 'priority is' queries."""
    test_cases = [
        ("priority is high", 'high'),
        ("priority is highest", 'highest'),
        ("priority is medium", 'medium'),
        ("priority is low", 'low'),
        ("priority is lowest", 'lowest'),
        ("priority is none", 'none'),
    ]

    for query, expected_priority in test_cases:
        filter_obj = parse_line(query)
        assert isinstance(filter_obj, PriorityFilter)
        assert filter_obj.comparison == 'is'
        assert filter_obj.target_priority == expected_priority


def test_parse_priority_above():
    """Test parsing 'priority is above' query."""
    filter_obj = parse_line("priority is above none")
    assert isinstance(filter_obj, PriorityFilter)
    assert filter_obj.comparison == 'above'
    assert filter_obj.target_priority == 'none'


def test_parse_priority_below():
    """Test parsing 'priority is below' query."""
    filter_obj = parse_line("priority is below medium")
    assert isinstance(filter_obj, PriorityFilter)
    assert filter_obj.comparison == 'below'
    assert filter_obj.target_priority == 'medium'


def test_parse_priority_not():
    """Test parsing 'priority is not' query."""
    filter_obj = parse_line("priority is not high")
    assert isinstance(filter_obj, PriorityFilter)
    assert filter_obj.comparison == 'is_not'
    assert filter_obj.target_priority == 'high'


def test_parse_boolean_and():
    """Test parsing boolean AND expression."""
    filter_obj = parse_line("(due after tomorrow) AND (due before in two weeks)")
    assert isinstance(filter_obj, AndFilter)
    assert len(filter_obj.filters) == 2
    assert isinstance(filter_obj.filters[0], DateFilter)
    assert isinstance(filter_obj.filters[1], DateFilter)


def test_parse_case_insensitive():
    """Test that parsing is case-insensitive."""
    filter1 = parse_line("DONE")
    filter2 = parse_line("Done")
    filter3 = parse_line("done")

    assert all(isinstance(f, StatusFilter) for f in [filter1, filter2, filter3])


def test_parse_multiline_query():
    """Test parsing multi-line query."""
    query_source = """not done
happens on today"""

    query = parse_query(query_source)
    assert query.error is None
    assert len(query.filters) == 2
    assert isinstance(query.filters[0], StatusFilter)
    assert isinstance(query.filters[1], HappensFilter)


def test_parse_complex_agenda_queries():
    """Test parsing actual Agenda.md queries."""
    # Overdue query
    query1 = parse_query("not done\nhappens before today")
    assert query1.error is None
    assert len(query1.filters) == 2

    # High priority 7 days query
    query2 = parse_query("""not done
happens AFTER yesterday
happens BEFORE in one week
priority is above none""")
    assert query2.error is None
    assert len(query2.filters) == 4

    # No deadline query
    query3 = parse_query("""not done
no due date
no scheduled date""")
    assert query3.error is None
    assert len(query3.filters) == 3


def test_parse_invalid_line():
    """Test parsing invalid query line."""
    filter_obj = parse_line("this is not a valid query")
    assert filter_obj is None


def test_parse_query_with_error():
    """Test parsing query with invalid lines."""
    query_source = """done
invalid line here
happens today"""

    query = parse_query(query_source)
    assert query.error is not None
    assert "Could not parse line" in query.error


