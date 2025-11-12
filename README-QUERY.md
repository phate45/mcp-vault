# Task Querying Documentation

**Version:** 0.2.0
**Status:** Production Ready

---

## Overview

The task querying module provides a standalone query engine for Obsidian vault tasks, compatible with the [Obsidian Tasks plugin](https://github.com/obsidian-tasks-group/obsidian-tasks) query syntax. It parses markdown checkbox tasks with emoji metadata and executes complex queries with filtering logic.

### Key Features

- **Task Parsing** - Extract tasks from markdown with emoji fields (priorities, dates)
- **Query Execution** - Filter tasks by status, dates, priority, presence/absence of fields
- **Boolean Logic** - Combine filters with AND/OR operators
- **Relative Dates** - Hardcoded support for today, tomorrow, yesterday, in one week, in two weeks
- **Standalone CLI** - Query tasks from the command line with JSON or text output
- **Location Tracking** - File path and line number for each task
- **Smart Filtering** - Automatically filters out malformed/empty tasks
- **Clean API** - Simple Python interface for programmatic use
- **MCP Ready** - Architecture prepared for future MCP tool integration

---

## Quick Reference

**Command pattern:**
```bash
uv run python -m mcp_vault.tasks.cli "query" <path>
```

**Output formats:**
- **JSON** (default) - Structured output with human-readable status/priority, null dates hidden
- **JSON with `--full`** - Include all fields including null dates
- **Raw text** (`--raw` flag) - Legacy human-readable format

**Filtering:**
- `--filter <paths>` - Exclude tasks from files with matching path prefixes (comma-separated)

---

## Installation

No installation required beyond the main `mcp-vault` dependencies. Run the query tool directly:

```bash
uv run python -m mcp_vault.tasks.cli "not done" /path/to/vault
```

---

## Quick Start

### CLI Usage

```bash
# Simple query with explicit vault path (JSON output)
uv run python -m mcp_vault.tasks.cli "not done" /path/to/vault

# Raw text output
uv run python -m mcp_vault.tasks.cli --raw "not done" /path/to/vault

# Filter out tasks from .claude directory
uv run python -m mcp_vault.tasks.cli --filter .claude "not done" /path/to/vault

# Filter multiple paths
uv run python -m mcp_vault.tasks.cli --filter '.claude,archived' "not done" /path/to/vault

# Using VAULT_PATH environment variable
VAULT_PATH=/path/to/vault uv run python -m mcp_vault.tasks.cli "not done"

# Multi-line query via stdin
echo -e "not done\nhappens today" | VAULT_PATH=/path/to/vault uv run python -m mcp_vault.tasks.cli
```

### Python API Usage

```python
from pathlib import Path
from mcp_vault.tasks import query

# Execute a query
vault_path = Path("/path/to/vault")
results = query(vault_path, "not done\nhappens today")

# Process results
for task in results:
    print(f"[{task.status}] {task.description}")
    print(f"  Due: {task.due_date}")
    print(f"  Priority: {task.priority}")
```

---

## Query Syntax Reference

### Status Filters

```
done                    # Completed tasks (status = 'x')
not done                # Incomplete tasks (status != 'x')
```

### Date Filters

**Field-specific date filters:**

```
due before <date>       # Due date is before target
due after <date>        # Due date is after target
due on <date>           # Due date equals target

scheduled before <date> # Scheduled date filters
scheduled after <date>
scheduled on <date>

start before <date>     # Start date filters
start after <date>
start on <date>

done on <date>          # Done date filters
done before <date>
done after <date>
```

**Happens filter (checks ANY of start/scheduled/due):**

```
happens before <date>   # Any date is before target
happens after <date>    # Any date is after target
happens on <date>       # Any date equals target
```

### Supported Date Formats

**Relative dates:**
- `today`
- `tomorrow`
- `yesterday`
- `in one week`
- `in two weeks`

**Absolute dates:**
- `2025-11-12` (YYYY-MM-DD format)

**Case insensitive:** `TODAY`, `Today`, and `today` all work

### Priority Filters

```
priority is highest     # Exact match
priority is high
priority is medium
priority is low
priority is lowest
priority is none

priority is not high    # Negation

priority is above none  # Comparison (above = higher priority)
priority is below medium
```

**Priority hierarchy (for comparisons):**
```
highest > high > medium > none > low > lowest
```

### Presence/Absence Filters

```
has due date            # Task has due date
no due date             # Task has no due date

has scheduled date      # Other date fields
no scheduled date
has start date
no start date
has done date
no done date
```

### Boolean Expressions

**Multi-line queries (implicit AND):**

```
not done
has due date
priority is high
```

All conditions must be true (filters applied sequentially).

**Explicit AND/OR:**

```
(due after tomorrow) AND (due before in two weeks)
(priority is high) OR (priority is highest)
```

**Notes:**
- Parentheses required for each sub-expression
- AND/OR are case-insensitive
- Can nest: `(filter1) AND ((filter2) OR (filter3))`

---

## Real-World Query Examples

### Agenda.md-Style Queries

**Overdue tasks:**
```
not done
happens before today
```

**Today's tasks:**
```
not done
happens on today
```

**High priority items (next 7 days):**
```
not done
happens after yesterday
happens before in one week
priority is above none
```

**Due in next 2 weeks (lower priority):**
```
not done
(due after tomorrow) AND (due before in two weeks)
priority is below medium
```

**Tasks without deadlines:**
```
not done
no due date
no scheduled date
```

**Recently completed:**
```
done on today
```

### Other Useful Queries

**High priority incomplete tasks:**
```
not done
priority is high
```

**Tasks with any date:**
```
not done
has due date
```

**All incomplete tasks:**
```
not done
```

---

## Task Markdown Format

### Basic Task Structure

```markdown
- [ ] Task description
- [x] Completed task
- [/] In progress task
- [-] Cancelled task
```

### With Emoji Metadata

```markdown
- [ ] Task with due date 📅 2025-11-15
- [ ] High priority task ⏫ 📅 2025-11-13
- [x] Completed task ✅ 2025-11-12
- [ ] Task with created and scheduled ➕ 2025-11-04 ⏳ 2025-11-12
- [ ] Full metadata 🔺 🛫 2025-11-12 ⏳ 2025-11-13 📅 2025-11-15
```

### Supported Emojis

**Priority:**
- 🔺 - Highest priority
- ⏫ - High priority
- 🔼 - Medium priority
- 🔽 - Low priority
- ⏬ - Lowest priority

**Dates:**
- 🛫 - Start date (YYYY-MM-DD)
- ⏳ / ⌛ - Scheduled date
- 📅 / 📆 / 🗓 - Due date
- ✅ - Done date
- ➕ - Created date

**Notes:**
- Emoji variant selector (`\uFE0F`) is handled automatically
- Multiple alternative emojis supported (e.g., ⏳ or ⌛ for scheduled)
- Date format must be YYYY-MM-DD
- Fields are extracted from end of line in specific order

---

## Architecture Overview

### Module Structure

```
src/mcp_vault/tasks/
├── __init__.py          # Public API (query function)
├── models.py            # Task/Query dataclasses, constants
├── parser.py            # Markdown task parsing
├── date_resolver.py     # Relative date resolution
├── filters.py           # Filter implementations
├── query_parser.py      # Query string parsing
├── executor.py          # Vault reading & filtering
└── cli.py               # Standalone CLI

tests/
├── fixtures/tasks/      # Test markdown files
│   ├── basic_tasks.md
│   ├── date_tasks.md
│   ├── priority_tasks.md
│   ├── mixed_tasks.md
│   └── edge_cases.md
├── test_task_parser.py
├── test_date_resolver.py
├── test_filters.py
├── test_query_parser.py
└── test_executor.py
```

### Design Principles

1. **Stdlib Only** - No external dependencies (dateparser, etc.)
2. **Sequential Filtering** - Filters applied in order for correctness
3. **Extensible** - Easy to add new date strings or filter types
4. **Testable** - Clean separation of concerns, comprehensive tests
5. **MCP Ready** - Public API designed for future tool integration

### Query Execution Flow

```
User Query String
    ↓
parse_query() - Parse into Filter objects
    ↓
read_vault_tasks() - Read all markdown files, extract tasks
    ↓
apply_filters() - Apply each filter sequentially
    ↓
Filtered Task List
```

### Filter Types

- **StatusFilter** - Match done/not done
- **DateFilter** - Match specific date fields with operators
- **HappensFilter** - Match ANY of start/scheduled/due
- **PriorityFilter** - Match priority levels with comparisons
- **HasFilter** - Match presence/absence of fields
- **AndFilter** - Combine filters with AND logic
- **OrFilter** - Combine filters with OR logic
- **NotFilter** - Negate a filter

---

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_task_parser.py -v

# Run specific test
uv run pytest tests/test_task_parser.py::test_parse_simple_task -v

# Run with short traceback
uv run pytest tests/ -v --tb=short
```

### Test Coverage

- **94 test cases** across 6 test files
- **Unit tests** for each module (parser, dates, filters, query parsing)
- **Integration tests** with real markdown fixtures
- **CLI tests** for flag parsing and path filtering
- **Edge cases** - variant selectors, alternative emojis, malformed tasks

### Test Fixtures

The `tests/fixtures/tasks/` directory contains comprehensive test data:
- Basic tasks with various statuses
- Tasks with date emojis (due, scheduled, start, done)
- Tasks with priority levels
- Mixed real-world examples
- Edge cases and malformed tasks

---

## CLI Reference

### Usage

```bash
uv run python -m mcp_vault.tasks.cli <query> [vault_path]
echo <query> | uv run python -m mcp_vault.tasks.cli [vault_path]
```

### Arguments

- `<query>` - Query string (use `\n` for multi-line, or pipe via stdin)
- `[vault_path]` - Optional vault path (defaults to VAULT_PATH env var)

### Flags

- `--raw` - Output in legacy text format instead of JSON
- `--filter <paths>` - Exclude tasks from files with matching path prefixes
  - Multiple paths separated by commas (e.g., `.claude,archived`)
  - Prefix matching: `--filter project` excludes `project/` and `project-archived/`
  - Whitespace around commas is trimmed automatically
  - At least one path required when flag is used
- `--full` - Include all fields in JSON output, even if null
  - By default, null date fields are hidden
  - With `--full`, all date fields are shown (including nulls)

### Environment Variables

- `VAULT_PATH` - Default vault path if not provided as argument

### Output Formats

**JSON (default):**

```json
{
  "tasks": [
    {
      "status": "Open",
      "description": "Review pull request",
      "priority": "High",
      "file_path": "mixed_tasks.md",
      "line_number": 8,
      "due_date": "2025-11-13",
      "created_date": "2025-11-04"
    }
  ],
  "count": 1
}
```

**Note:** By default, null date fields are hidden. Only dates with values are shown. Use `--full` to include all date fields.

**JSON (with `--full` flag):**

```json
{
  "tasks": [
    {
      "status": "Open",
      "description": "Review pull request",
      "priority": "High",
      "file_path": "mixed_tasks.md",
      "line_number": 8,
      "start_date": null,
      "scheduled_date": null,
      "due_date": "2025-11-13",
      "done_date": null,
      "created_date": "2025-11-04"
    }
  ],
  "count": 1
}
```

**Raw text (with `--raw` flag):**

```
[x] Completed task (📅 2025-11-12)
[ ] Pending task (📅 2025-11-15, ⏳ 2025-11-13)

Found N task(s)  # Summary line on stderr
```

**Field Transformations:**
- **Status**: Converted to human-readable values:
  - ` ` (space) → `"Open"`
  - `/` → `"In Progress"`
  - `x` → `"Done"`
  - `-` → `"Cancelled"`
  - Other characters → `"Custom (X)"` where X is the character
- **Priority**: Null priorities shown as `"Normal"`, others capitalized (e.g., `"High"`, `"Highest"`)
- **Dates**: Null dates hidden by default (use `--full` to show them)

**Task Filtering:**
- Tasks with empty descriptions are automatically filtered out
- Only valid tasks (with non-empty description) are included in results
- Use `--filter` flag to exclude tasks by file path prefix (see Flags section)

### Exit Codes

- `0` - Success (tasks found or no tasks matching)
- `1` - Error (parse error, vault not found, etc.)

### Examples

```bash
# Simple query with explicit path
uv run python -m mcp_vault.tasks.cli "not done" /home/user/vault

# Multi-line query (use bash $'...' syntax for newlines)
uv run python -m mcp_vault.tasks.cli $'not done\nhas due date' /home/user/vault

# Or use stdin
echo -e "not done\nhas due date" | \
    uv run python -m mcp_vault.tasks.cli /home/user/vault

# With VAULT_PATH env var (no path needed)
VAULT_PATH=/home/user/vault uv run python -m mcp_vault.tasks.cli "priority is high"

# Exclude tasks from specific directories
uv run python -m mcp_vault.tasks.cli --filter '.claude,archive' "not done" /home/user/vault

# Combine with raw output
uv run python -m mcp_vault.tasks.cli --raw --filter templates "happens today" /home/user/vault

# Show all fields including nulls
uv run python -m mcp_vault.tasks.cli --full "not done" /home/user/vault
```

---

## Python API Reference

### Main Function

```python
def query(vault_path: Path, query_source: str) -> List[Task]
```

Execute a query against all tasks in the vault.

**Parameters:**
- `vault_path` (Path) - Path to the Obsidian vault root directory
- `query_source` (str) - Query string (multi-line, one filter per line)

**Returns:**
- `List[Task]` - List of Task objects matching the query

**Raises:**
- `ValueError` - If the query cannot be parsed

**Example:**
```python
from pathlib import Path
from mcp_vault.tasks import query

vault = Path("/home/user/vault")
results = query(vault, "not done\nhappens today")

for task in results:
    print(task.description)
```

### Task Object

```python
@dataclass
class Task:
    status: str                    # 'x', ' ', '/', '-', 'Q', etc.
    description: str               # Task text after emoji fields
    priority: Optional[str]        # 'highest', 'high', 'medium', 'low', 'lowest', None
    start_date: Optional[date]     # 🛫 YYYY-MM-DD
    scheduled_date: Optional[date] # ⏳ YYYY-MM-DD
    due_date: Optional[date]       # 📅 YYYY-MM-DD
    done_date: Optional[date]      # ✅ YYYY-MM-DD
    created_date: Optional[date]   # ➕ YYYY-MM-DD
    source_line: str               # Original markdown line
    file_path: str                 # Path to file (relative to vault root)
    line_number: int               # Line number in file (1-indexed)

    @property
    def is_done(self) -> bool:
        """Check if task is marked as done."""

    def is_valid(self) -> bool:
        """Check if task has non-empty description."""
```

**Note:** The Task dataclass represents the internal Python model. When outputting to JSON via the CLI:
- The `status` field is transformed to human-readable strings (`"Open"`, `"In Progress"`, `"Done"`, `"Cancelled"`)
- The `priority` field is capitalized and null values become `"Normal"`
- Null date fields are hidden by default (unless `--full` flag is used)

### Additional Functions

```python
def read_vault_tasks(vault_path: Path) -> List[Task]
```

Read all tasks from markdown files in the vault (without filtering).

```python
def execute_query(tasks: List[Task], query_source: str) -> List[Task]
```

Execute a query against a pre-loaded list of tasks.

---

## Future Extensions

### Adding New Relative Dates

Edit `src/mcp_vault/tasks/date_resolver.py`:

```python
RELATIVE_DATE_MAP = {
    'today': lambda ref: ref,
    'tomorrow': lambda ref: ref + timedelta(days=1),
    # Add new mappings:
    'in 3 days': lambda ref: ref + timedelta(days=3),
    'next monday': lambda ref: ...,  # Implement logic
}
```

### Adding New Filter Types

1. Create filter class in `src/mcp_vault/tasks/filters.py`:

```python
class RecurringFilter(Filter):
    def matches(self, task: Task) -> bool:
        # Check if task has recurrence info
        return task.recurrence is not None  # (if field added)
```

2. Add pattern to `src/mcp_vault/tasks/query_parser.py`:

```python
RECURRING_PATTERN = re.compile(r'^is recurring$', re.IGNORECASE)

# In parse_line():
if RECURRING_PATTERN.match(line):
    return RecurringFilter()
```

### MCP Tool Integration

When ready to add MCP tool (not in current scope):

```python
# In src/mcp_vault/tools.py

class QueryTasksTool(ToolHandler):
    def __init__(self, context: ToolContext):
        super().__init__("query_tasks", context)

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Query tasks in the vault with Obsidian Tasks syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Multi-line query string"
                    }
                },
                "required": ["query"]
            }
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        from .tasks import query
        results = query(self.context.vault_path, args['query'])

        # Format results
        formatted = []
        for task in results:
            line = f"[{task.status}] {task.description}"
            if task.due_date:
                line += f" 📅 {task.due_date}"
            formatted.append(line)

        return [TextContent(type="text", text="\n".join(formatted))]

# Don't forget to register in register_tools()
```

---

## Troubleshooting

### Parse Errors

**Query parse error: Could not parse line: X**

- Check query syntax against examples above
- Ensure relative dates are spelled correctly (case-insensitive)
- Verify boolean expressions have proper parentheses
- For multi-line queries from command line, use stdin (echo -e) or proper escaping

### No Tasks Found

- Verify vault path is correct
- Check that markdown files contain checkbox tasks (`- [ ]` or `- [x]`)
- Ensure date emojis are followed by YYYY-MM-DD format
- Test with simpler query first: `mcp-vault-query "not done"`

### Import Errors

If Python can't find modules:

```bash
# Ensure you're in the project directory
cd /path/to/mcp-vault

# Run with uv
uv run python -c "from mcp_vault.tasks import query; print('OK')"
```

## Contributing

When extending the query engine:

1. Add tests first (TDD approach)
2. Maintain backward compatibility
3. Update this documentation
4. Run full test suite before committing

