"""Task markdown parsing with emoji field extraction."""

from datetime import date
from typing import Optional
from .models import (
    Task,
    TASK_REGEX,
    PRIORITY_REGEX,
    PRIORITY_EMOJI_MAP,
    DONE_DATE_REGEX,
    SCHEDULED_DATE_REGEX,
    DUE_DATE_REGEX,
    START_DATE_REGEX,
    CREATED_DATE_REGEX,
)


def parse_task_line(line: str, file_path: str = "", line_number: int = 0) -> Optional[Task]:
    """Parse a markdown line into a Task object.

    Args:
        line: A markdown line that may contain a task
        file_path: Path to the file (relative to vault root)
        line_number: Line number in file (1-indexed)

    Returns:
        Task object if line is a valid task, None otherwise
    """
    # Match the main task pattern
    match = TASK_REGEX.match(line)
    if not match:
        return None

    # Extract components
    # indentation = match.group(1)  # Not needed for now
    # list_marker = match.group(2)  # Not needed for now
    status_char = match.group(3)
    content = match.group(4)

    # Reject invalid status characters (e.g., '[' or ']' from wiki links)
    # Valid status characters are typically: space, x, /, -, letters, etc.
    # But NOT brackets which would indicate a wiki link like [[]]
    if status_char in ['[', ']']:
        return None

    # Extract emoji fields from the content
    fields, description = extract_emoji_fields(content)

    # Build the Task object
    return Task(
        status=status_char,
        description=description.strip(),
        priority=fields.get('priority'),
        start_date=fields.get('start_date'),
        scheduled_date=fields.get('scheduled_date'),
        due_date=fields.get('due_date'),
        done_date=fields.get('done_date'),
        created_date=fields.get('created_date'),
        source_line=line,
        file_path=file_path,
        line_number=line_number,
    )


def extract_emoji_fields(content: str) -> tuple[dict, str]:
    """Extract emoji fields from task content.

    Fields are removed from the end of the string in a specific order.
    Loop up to 20 times to catch all fields.

    Args:
        content: The task content after the checkbox

    Returns:
        Tuple of (extracted_fields_dict, remaining_description)
    """
    fields = {
        'priority': None,
        'done_date': None,
        'scheduled_date': None,
        'due_date': None,
        'start_date': None,
        'created_date': None,
    }

    remaining = content.strip()

    # Loop up to 20 times to extract all fields
    # (matching the plugin's behavior)
    for _ in range(20):
        if not remaining:
            break

        # Try each pattern in order
        found = False

        # Priority emoji (must come first as it has no date)
        match = PRIORITY_REGEX.search(remaining)
        if match and fields['priority'] is None:
            emoji = match.group(1)
            fields['priority'] = priority_emoji_to_name(emoji)
            remaining = remaining[:match.start()].strip()
            found = True
            continue

        # Done date
        match = DONE_DATE_REGEX.search(remaining)
        if match and fields['done_date'] is None:
            date_str = match.group(1)
            fields['done_date'] = parse_date(date_str)
            remaining = remaining[:match.start()].strip()
            found = True
            continue

        # Scheduled date
        match = SCHEDULED_DATE_REGEX.search(remaining)
        if match and fields['scheduled_date'] is None:
            date_str = match.group(1)
            fields['scheduled_date'] = parse_date(date_str)
            remaining = remaining[:match.start()].strip()
            found = True
            continue

        # Due date
        match = DUE_DATE_REGEX.search(remaining)
        if match and fields['due_date'] is None:
            date_str = match.group(1)
            fields['due_date'] = parse_date(date_str)
            remaining = remaining[:match.start()].strip()
            found = True
            continue

        # Start date
        match = START_DATE_REGEX.search(remaining)
        if match and fields['start_date'] is None:
            date_str = match.group(1)
            fields['start_date'] = parse_date(date_str)
            remaining = remaining[:match.start()].strip()
            found = True
            continue

        # Created date
        match = CREATED_DATE_REGEX.search(remaining)
        if match and fields['created_date'] is None:
            date_str = match.group(1)
            fields['created_date'] = parse_date(date_str)
            remaining = remaining[:match.start()].strip()
            found = True
            continue

        # If no field was found, break the loop
        if not found:
            break

    return fields, remaining


def priority_emoji_to_name(emoji: str) -> str:
    """Convert priority emoji to priority name.

    Args:
        emoji: Priority emoji character

    Returns:
        Priority name: 'highest', 'high', 'medium', 'low', 'lowest'
    """
    # Remove variant selector if present
    emoji = emoji.replace('\uFE0F', '')
    return PRIORITY_EMOJI_MAP.get(emoji, 'none')


def parse_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD date string into date object.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        date object, or None if invalid
    """
    try:
        year, month, day = date_str.split('-')
        return date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return None
