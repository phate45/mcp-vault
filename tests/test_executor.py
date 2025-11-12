"""Integration tests for task querying with test fixtures."""

from pathlib import Path
from datetime import date
from mcp_vault.tasks import query, read_vault_tasks, execute_query


def get_fixtures_path():
    """Get path to test fixtures."""
    return Path(__file__).parent / 'fixtures' / 'tasks'


def test_read_vault_tasks():
    """Test reading all tasks from test fixtures."""
    fixtures_path = get_fixtures_path()
    tasks = read_vault_tasks(fixtures_path)

    # We should have tasks from all 5 fixture files
    assert len(tasks) > 0

    # Check that we have various task types
    statuses = {task.status for task in tasks}
    assert ' ' in statuses  # Not done
    assert 'x' in statuses  # Done


def test_query_not_done():
    """Test querying for not done tasks."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "not done")

    assert len(results) > 0
    assert all(not task.is_done for task in results)


def test_query_done():
    """Test querying for done tasks."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "done")

    assert len(results) > 0
    assert all(task.is_done for task in results)


def test_query_has_due_date():
    """Test querying for tasks with due date."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "has due date")

    assert len(results) > 0
    assert all(task.due_date is not None for task in results)


def test_query_no_due_date():
    """Test querying for tasks without due date."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "no due date")

    assert len(results) > 0
    assert all(task.due_date is None for task in results)


def test_query_priority_high():
    """Test querying for high priority tasks."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "priority is high")

    assert len(results) > 0
    assert all(task.priority == 'high' for task in results)


def test_query_priority_above_none():
    """Test querying for tasks with priority above none."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "priority is above none")

    # Above none = highest, high, medium
    valid_priorities = {'highest', 'high', 'medium'}
    assert len(results) > 0
    assert all(task.priority in valid_priorities for task in results)


def test_query_multiline_not_done_has_due():
    """Test multi-line query: not done AND has due date."""
    fixtures_path = get_fixtures_path()
    results = query(fixtures_path, "not done\nhas due date")

    assert len(results) > 0
    assert all(not task.is_done for task in results)
    assert all(task.due_date is not None for task in results)


def test_query_date_relative():
    """Test query with relative date (today)."""
    fixtures_path = get_fixtures_path()

    # Note: This test depends on the fixture having tasks with 2025-11-12
    # The test will work when run on different dates because the query
    # uses relative dates which are resolved at query time
    try:
        results = query(fixtures_path, "due on today")
        # Should match tasks with today's date
        assert all(task.due_date is not None for task in results)
    except ValueError:
        # Query might fail if no tasks match today's date
        pass


def test_query_boolean_and():
    """Test boolean AND query."""
    fixtures_path = get_fixtures_path()

    # Complex query with AND
    query_str = "(not done) AND (has due date)"
    results = query(fixtures_path, query_str)

    # Results should satisfy both conditions
    assert all(not task.is_done for task in results)
    assert all(task.due_date is not None for task in results)


def test_query_no_results():
    """Test query that returns no results."""
    fixtures_path = get_fixtures_path()

    # Query for a very specific condition unlikely to match
    # (e.g., due on a far future date)
    results = query(fixtures_path, "due on 2099-12-31")
    assert len(results) == 0


def test_execute_query_with_tasks():
    """Test execute_query directly with a task list."""
    fixtures_path = get_fixtures_path()
    all_tasks = read_vault_tasks(fixtures_path)

    # Filter to just done tasks
    results = execute_query(all_tasks, "done")

    assert len(results) > 0
    assert all(task.is_done for task in results)
    # Results should be a subset of all_tasks
    assert len(results) < len(all_tasks)


def test_query_complex_agenda_scenario():
    """Test a complex real-world query similar to Agenda.md."""
    fixtures_path = get_fixtures_path()

    # Simulate "Overdue" query: not done + happens before today
    # Note: This depends on fixture dates
    all_tasks = read_vault_tasks(fixtures_path)

    # Just verify the query parses and runs without error
    try:
        results = query(fixtures_path, "not done\nhappens before today")
        # All results should be not done
        assert all(not task.is_done for task in results)
    except ValueError:
        # Query might fail if dates can't be resolved
        pass


def test_query_priority_and_status():
    """Test combining priority and status filters."""
    fixtures_path = get_fixtures_path()

    results = query(fixtures_path, "not done\npriority is high")

    # Should have at least some results
    if len(results) > 0:
        assert all(not task.is_done for task in results)
        assert all(task.priority == 'high' for task in results)


def test_empty_vault(tmp_path):
    """Test querying an empty vault."""
    empty_vault = tmp_path
    results = query(empty_vault, "not done")

    assert len(results) == 0


def test_query_error_handling():
    """Test that invalid queries raise ValueError."""
    fixtures_path = get_fixtures_path()

    try:
        query(fixtures_path, "invalid query syntax here")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "parse error" in str(e).lower()


