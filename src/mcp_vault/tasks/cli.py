"""Standalone CLI for task querying."""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import date
from . import query


def task_to_dict(task, full=False):
    """Convert Task object to JSON-serializable dict.

    Args:
        task: Task object to convert
        full: If True, include all fields even if null. If False, hide null dates.
    """
    # Status character to human-readable mapping
    STATUS_MAP = {
        ' ': 'Open',
        '/': 'In Progress',
        'x': 'Done',
        '-': 'Cancelled',
    }

    # Convert status character to human-readable string
    status_str = STATUS_MAP.get(task.status, f'Custom ({task.status})')

    # Convert priority
    if task.priority is None:
        priority_str = 'Normal'
    else:
        priority_str = task.priority.capitalize()

    # Build result dictionary
    result = {
        'status': status_str,
        'description': task.description,
        'priority': priority_str,
        'file_path': task.file_path,
        'line_number': task.line_number,
    }

    # Add date fields (conditionally include nulls)
    date_fields = [
        ('start_date', task.start_date),
        ('scheduled_date', task.scheduled_date),
        ('due_date', task.due_date),
        ('done_date', task.done_date),
        ('created_date', task.created_date),
    ]

    for field_name, field_value in date_fields:
        if full or field_value is not None:
            result[field_name] = field_value.isoformat() if field_value else None

    return result


def main():
    """Main entry point for mcp-vault-query CLI.

    Usage:
        mcp-vault-query "not done"
        mcp-vault-query --raw "not done"
        mcp-vault-query --filter .claude "not done"
        mcp-vault-query --filter .claude,archived "not done"
        mcp-vault-query "happens today" /path/to/vault
        echo "not done" | mcp-vault-query
    """
    # Create argument parser
    parser = argparse.ArgumentParser(
        prog='mcp-vault-query',
        description='Query tasks in an Obsidian vault',
        add_help=True
    )

    parser.add_argument(
        '--raw',
        action='store_true',
        help='Output in legacy text format instead of JSON'
    )

    parser.add_argument(
        '--filter',
        metavar='PATHS',
        help='Exclude tasks from files starting with given path(s). Multiple paths separated by commas'
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='Include all fields in JSON output, even if null'
    )

    parser.add_argument(
        'query',
        nargs='?',
        default=None,
        help='Task query string (reads from stdin if not provided)'
    )

    parser.add_argument(
        'vault_path',
        nargs='?',
        default=None,
        help='Path to vault (defaults to VAULT_PATH environment variable)'
    )

    # Parse arguments
    args = parser.parse_args()

    # Determine query source
    query_source = args.query
    if query_source is None:
        # Read from stdin
        query_source = sys.stdin.read().strip()

    # Parse filter paths if provided
    filter_paths = []
    if args.filter:
        filter_paths = [p.strip() for p in args.filter.split(',') if p.strip()]
        if not filter_paths:
            print("Error: --filter requires at least one non-empty path", file=sys.stderr)
            return 1

    # Determine vault path
    vault_path = args.vault_path
    if vault_path is None:
        vault_path_str = os.getenv('VAULT_PATH')
        if not vault_path_str:
            print("Error: VAULT_PATH environment variable not set and vault path not provided", file=sys.stderr)
            return 1
        vault_path = vault_path_str

    vault_path = Path(vault_path)

    # Validate vault path
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}", file=sys.stderr)
        return 1

    if not vault_path.is_dir():
        print(f"Error: Vault path is not a directory: {vault_path}", file=sys.stderr)
        return 1

    # Execute query
    try:
        results = query(vault_path, query_source)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    # Apply path filters if specified
    if filter_paths:
        results = [
            task for task in results
            if not any(task.file_path.startswith(filter_path) for filter_path in filter_paths)
        ]

    # Format and print results
    if not results:
        if args.raw:
            print("No tasks found matching query.", file=sys.stderr)
        else:
            print(json.dumps({"tasks": [], "count": 0}))
        return 0

    if args.raw:
        # Legacy text format
        for task in results:
            # Format: [status] description (dates)
            status_symbol = 'x' if task.is_done else ' '
            output = f"[{status_symbol}] {task.description}"

            # Add date info if present
            date_parts = []
            if task.due_date:
                date_parts.append(f"📅 {task.due_date}")
            if task.scheduled_date:
                date_parts.append(f"⏳ {task.scheduled_date}")
            if task.start_date:
                date_parts.append(f"🛫 {task.start_date}")

            if date_parts:
                output += " (" + ", ".join(date_parts) + ")"

            print(output)

        # Print summary
        print(f"\nFound {len(results)} task(s)", file=sys.stderr)
    else:
        # JSON format (default)
        output = {
            "tasks": [task_to_dict(task, full=args.full) for task in results],
            "count": len(results)
        }
        print(json.dumps(output, indent=2))

    return 0


if __name__ == '__main__':
    sys.exit(main())
