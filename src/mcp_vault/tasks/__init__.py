"""Task querying module for Obsidian vault.

This module provides task parsing and querying functionality compatible with
the Obsidian Tasks plugin query syntax. It supports:

- Parsing markdown checkbox tasks with emoji fields (priorities, dates)
- Querying tasks with status, date, priority, and boolean filters
- Hardcoded relative date resolution (today, tomorrow, etc.)

Example usage:
    from pathlib import Path
    from mcp_vault.tasks import query

    vault_path = Path("/path/to/vault")
    results = query(vault_path, "not done\\nhappens today")

    for task in results:
        print(task.description)
"""

from pathlib import Path
from typing import List

from .models import Task, Query
from .filters import Filter
from .executor import read_vault_tasks, execute_query


def query(vault_path: Path, query_source: str) -> List[Task]:
    """Execute a query against all tasks in the vault.

    This is the main entry point for the tasks module. It reads all tasks
    from markdown files in the vault and applies the specified query filters.

    Args:
        vault_path: Path to the Obsidian vault root directory
        query_source: Query string (multi-line, one filter per line)

    Returns:
        List of Task objects matching the query

    Raises:
        ValueError: If the query cannot be parsed

    Example:
        results = query(Path("/vault"), "not done\\nhappens today")
    """
    tasks = read_vault_tasks(vault_path)
    return execute_query(tasks, query_source)


# Public API exports
__all__ = [
    'query',
    'Task',
    'Query',
    'Filter',
    'read_vault_tasks',
    'execute_query',
]
