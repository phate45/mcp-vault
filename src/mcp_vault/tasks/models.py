"""Core data models for task querying."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
import re


@dataclass
class Task:
    """Represents a parsed task from markdown."""

    status: str  # 'x', ' ', '/', '-', 'Q', etc.
    description: str  # Task text after emoji fields
    priority: Optional[str]  # 'highest', 'high', 'medium', 'low', 'lowest', None
    start_date: Optional[date]  # 🛫 YYYY-MM-DD
    scheduled_date: Optional[date]  # ⏳ YYYY-MM-DD
    due_date: Optional[date]  # 📅 YYYY-MM-DD
    done_date: Optional[date]  # ✅ YYYY-MM-DD
    created_date: Optional[date]  # ➕ YYYY-MM-DD
    source_line: str  # Original markdown line
    file_path: str  # Path to file (relative to vault root)
    line_number: int  # Line number in file (1-indexed)

    @property
    def is_done(self) -> bool:
        """Check if task is marked as done."""
        return self.status == 'x'

    def is_valid(self) -> bool:
        """Check if task is valid (has non-empty description)."""
        return bool(self.description.strip())


@dataclass
class Query:
    """Represents a parsed query with filters."""

    filters: list  # List of Filter objects
    error: Optional[str] = None  # Parse error, if any


# Priority hierarchy for comparisons
# Lower value = higher priority
PRIORITY_HIERARCHY = {
    'highest': 0,
    'high': 1,
    'medium': 2,
    'none': 3,
    'low': 4,
    'lowest': 5,
}

# Priority emoji to name mapping
PRIORITY_EMOJI_MAP = {
    '🔺': 'highest',
    '⏫': 'high',
    '🔼': 'medium',
    '🔽': 'low',
    '⏬': 'lowest',
}

# Compiled regex patterns for task parsing
# Main task pattern: matches checkbox tasks
TASK_REGEX = re.compile(r'^([\s\t>]*)([-*+]|[0-9]+[.)]) +\[(.)\] *(.*)$')

# Emoji field patterns (applied from end of string)
# \uFE0F? handles optional Variant Selector 16
PRIORITY_REGEX = re.compile(r'(🔺|⏫|🔼|🔽|⏬)\uFE0F?$')
DONE_DATE_REGEX = re.compile(r'✅\uFE0F? *(\d{4}-\d{2}-\d{2})$')
SCHEDULED_DATE_REGEX = re.compile(r'(?:⏳|⌛)\uFE0F? *(\d{4}-\d{2}-\d{2})$')
DUE_DATE_REGEX = re.compile(r'(?:📅|📆|🗓)\uFE0F? *(\d{4}-\d{2}-\d{2})$')
START_DATE_REGEX = re.compile(r'🛫\uFE0F? *(\d{4}-\d{2}-\d{2})$')
CREATED_DATE_REGEX = re.compile(r'➕\uFE0F? *(\d{4}-\d{2}-\d{2})$')
