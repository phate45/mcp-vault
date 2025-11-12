"""Executor for reading vault tasks and applying query filters."""

from pathlib import Path
from typing import List
from .models import Task
from .parser import parse_task_line
from .query_parser import parse_query


def read_vault_tasks(vault_path: Path, filter_invalid: bool = True) -> List[Task]:
    """Read all tasks from markdown files in the vault.

    Args:
        vault_path: Path to the vault root directory
        filter_invalid: If True, filter out tasks with empty descriptions

    Returns:
        List of Task objects found in the vault
    """
    tasks = []

    # Recursively find all markdown files
    for md_file in vault_path.rglob("*.md"):
        # Get relative path from vault root
        try:
            relative_path = str(md_file.relative_to(vault_path))
        except ValueError:
            # File not under vault_path (shouldn't happen with rglob)
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    task = parse_task_line(
                        line.rstrip('\n\r'),
                        file_path=relative_path,
                        line_number=line_num
                    )
                    if task is not None:
                        # Optionally filter out invalid tasks
                        if not filter_invalid or task.is_valid():
                            tasks.append(task)
        except (IOError, OSError) as e:
            # Skip files that can't be read
            continue

    return tasks


def execute_query(tasks: List[Task], query_source: str) -> List[Task]:
    """Execute a query against a list of tasks.

    Args:
        tasks: List of tasks to filter
        query_source: Query string to parse and execute

    Returns:
        Filtered list of tasks matching the query
    """
    # Parse the query
    query = parse_query(query_source)

    # Check for parse errors
    if query.error is not None:
        raise ValueError(f"Query parse error: {query.error}")

    # Apply filters sequentially
    return apply_filters(tasks, query.filters)


def apply_filters(tasks: List[Task], filters: List) -> List[Task]:
    """Apply a list of filters to tasks sequentially.

    Args:
        tasks: List of tasks to filter
        filters: List of Filter objects to apply

    Returns:
        Filtered list of tasks
    """
    result = tasks

    for filter_obj in filters:
        result = [task for task in result if filter_obj.matches(task)]

    return result
