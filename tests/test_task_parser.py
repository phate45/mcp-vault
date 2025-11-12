"""Unit tests for task parsing."""

from datetime import date
from mcp_vault.tasks.parser import parse_task_line, extract_emoji_fields, priority_emoji_to_name


def test_parse_simple_task():
    """Test parsing a simple task without emojis."""
    line = "- [ ] Simple task"
    task = parse_task_line(line)

    assert task is not None
    assert task.status == ' '
    assert task.description == "Simple task"
    assert task.priority is None
    assert task.due_date is None
    assert task.scheduled_date is None
    assert task.start_date is None
    assert task.done_date is None


def test_parse_completed_task():
    """Test parsing a completed task."""
    line = "- [x] Completed task"
    task = parse_task_line(line)

    assert task is not None
    assert task.status == 'x'
    assert task.is_done is True
    assert task.description == "Completed task"


def test_parse_task_with_due_date():
    """Test parsing task with due date."""
    line = "- [ ] Task with due date 📅 2025-11-12"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Task with due date"
    assert task.due_date == date(2025, 11, 12)


def test_parse_task_with_scheduled_date():
    """Test parsing task with scheduled date."""
    line = "- [ ] Task with scheduled date ⏳ 2025-11-13"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Task with scheduled date"
    assert task.scheduled_date == date(2025, 11, 13)


def test_parse_task_with_start_date():
    """Test parsing task with start date."""
    line = "- [ ] Task with start date 🛫 2025-11-14"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Task with start date"
    assert task.start_date == date(2025, 11, 14)


def test_parse_task_with_done_date():
    """Test parsing task with done date."""
    line = "- [x] Completed task ✅ 2025-11-12"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Completed task"
    assert task.done_date == date(2025, 11, 12)


def test_parse_task_with_created_date():
    """Test parsing task with created date."""
    line = "- [ ] Task with created date ➕ 2025-11-04"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Task with created date"
    assert task.created_date == date(2025, 11, 4)


def test_parse_task_with_priority():
    """Test parsing task with priority emoji."""
    test_cases = [
        ("- [ ] Highest priority 🔺", "highest"),
        ("- [ ] High priority ⏫", "high"),
        ("- [ ] Medium priority 🔼", "medium"),
        ("- [ ] Low priority 🔽", "low"),
        ("- [ ] Lowest priority ⏬", "lowest"),
    ]

    for line, expected_priority in test_cases:
        task = parse_task_line(line)
        assert task is not None
        assert task.priority == expected_priority


def test_parse_task_with_multiple_fields():
    """Test parsing task with multiple emoji fields."""
    line = "- [ ] Complex task 🔺 🛫 2025-11-12 ⏳ 2025-11-13 📅 2025-11-15"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Complex task"
    assert task.priority == "highest"
    assert task.start_date == date(2025, 11, 12)
    assert task.scheduled_date == date(2025, 11, 13)
    assert task.due_date == date(2025, 11, 15)


def test_parse_task_with_created_and_scheduled():
    """Test parsing task with created date and scheduled date (real-world example)."""
    line = "- [ ] Review sequential thinking MCP integration ➕ 2025-11-04 ⏳ 2025-11-12"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Review sequential thinking MCP integration"
    assert task.created_date == date(2025, 11, 4)
    assert task.scheduled_date == date(2025, 11, 12)


def test_parse_task_with_variant_selector():
    """Test parsing task with variant selector emoji."""
    # Use explicit unicode characters to ensure variant selector is present
    line = "- [ ] Task with variant 📅\uFE0F 2025-11-12"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Task with variant"
    assert task.due_date == date(2025, 11, 12)


def test_parse_task_with_alternative_emojis():
    """Test parsing task with alternative emoji representations."""
    # Alternative scheduled emoji
    line1 = "- [ ] Task scheduled ⌛ 2025-11-13"
    task1 = parse_task_line(line1)
    assert task1 is not None
    assert task1.scheduled_date == date(2025, 11, 13)

    # Alternative due emojis
    line2 = "- [ ] Task due 📆 2025-11-14"
    task2 = parse_task_line(line2)
    assert task2 is not None
    assert task2.due_date == date(2025, 11, 14)

    line3 = "- [ ] Task due 🗓 2025-11-15"
    task3 = parse_task_line(line3)
    assert task3 is not None
    assert task3.due_date == date(2025, 11, 15)


def test_parse_indented_task():
    """Test parsing indented task."""
    line = "  - [ ] Indented task"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Indented task"


def test_parse_blockquote_task():
    """Test parsing task in blockquote."""
    line = "> - [ ] Task in blockquote"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "Task in blockquote"


def test_parse_numbered_task():
    """Test parsing numbered list task."""
    line = "1. [ ] First numbered task"
    task = parse_task_line(line)

    assert task is not None
    assert task.description == "First numbered task"


def test_parse_non_task_lines():
    """Test that non-task lines return None."""
    non_tasks = [
        "This is a regular paragraph",
        "* This is a list item but not a task",
        "- This is a list item without checkbox",
        "",
        "# Heading",
    ]

    for line in non_tasks:
        task = parse_task_line(line)
        assert task is None


def test_parse_wiki_links_not_tasks():
    """Test that Obsidian wiki links are not parsed as tasks."""
    wiki_links = [
        "- [[]]",
        "- [[Some Link]]",
        "- [[Link|Alias]]",
        "* [[Another Link]]",
    ]

    for line in wiki_links:
        task = parse_task_line(line)
        assert task is None, f"Wiki link should not be parsed as task: {line}"


def test_extract_emoji_fields():
    """Test emoji field extraction."""
    content = "Task description 🔺 📅 2025-11-12"
    fields, description = extract_emoji_fields(content)

    assert description == "Task description"
    assert fields['priority'] == 'highest'
    assert fields['due_date'] == date(2025, 11, 12)


def test_priority_emoji_to_name():
    """Test priority emoji to name conversion."""
    assert priority_emoji_to_name('🔺') == 'highest'
    assert priority_emoji_to_name('⏫') == 'high'
    assert priority_emoji_to_name('🔼') == 'medium'
    assert priority_emoji_to_name('🔽') == 'low'
    assert priority_emoji_to_name('⏬') == 'lowest'


