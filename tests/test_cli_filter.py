"""Unit tests for CLI --filter functionality."""

import sys
import subprocess
from pathlib import Path
import json
import pytest


def run_cli(*args):
    """Helper to run the CLI and capture output."""
    result = subprocess.run(
        [sys.executable, '-m', 'mcp_vault.tasks.cli'] + list(args),
        capture_output=True,
        text=True
    )
    return result


def test_filter_single_path(tmp_path):
    """Test filtering with a single path prefix."""
    vault = tmp_path

    # Create tasks in .claude directory
    claude_dir = vault / '.claude'
    claude_dir.mkdir()
    (claude_dir / 'tasks.md').write_text('- [ ] Claude task\n')

    # Create tasks in root
    (vault / 'root.md').write_text('- [ ] Root task\n')

    # Query without filter - should see both
    result = run_cli('not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 2

    # Query with .claude filter - should only see root task
    result = run_cli('--filter', '.claude', 'not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 1
    assert data['tasks'][0]['description'] == 'Root task'
    assert data['tasks'][0]['file_path'] == 'root.md'


def test_filter_multiple_paths(tmp_path):
    """Test filtering with multiple comma-separated path prefixes."""
    vault = tmp_path

    # Create tasks in different directories
    (vault / '.claude').mkdir()
    (vault / '.claude' / 'tasks.md').write_text('- [ ] Claude task\n')

    (vault / 'archived').mkdir()
    (vault / 'archived' / 'old.md').write_text('- [ ] Archived task\n')

    (vault / 'active.md').write_text('- [ ] Active task\n')

    # Query without filter - should see all 3
    result = run_cli('not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 3

    # Query with multiple filters - should only see active task
    result = run_cli('--filter', '.claude,archived', 'not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 1
    assert data['tasks'][0]['description'] == 'Active task'


def test_filter_no_matches(tmp_path):
    """Test that filter with no matches returns all tasks."""
    vault = tmp_path
    (vault / 'tasks.md').write_text('- [ ] Task 1\n- [ ] Task 2\n')

    # Filter that doesn't match anything
    result = run_cli('--filter', 'nonexistent', 'not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 2


def test_filter_all_filtered(tmp_path):
    """Test filtering out all tasks."""
    vault = tmp_path

    (vault / '.claude').mkdir()
    (vault / '.claude' / 'tasks.md').write_text('- [ ] Task 1\n- [ ] Task 2\n')

    # Filter that matches all tasks
    result = run_cli('--filter', '.claude', 'not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 0
    assert data['tasks'] == []


def test_filter_with_spaces(tmp_path):
    """Test filtering paths with spaces (after comma splitting)."""
    vault = tmp_path

    (vault / 'dir1').mkdir()
    (vault / 'dir1' / 'tasks.md').write_text('- [ ] Task 1\n')

    (vault / 'dir2').mkdir()
    (vault / 'dir2' / 'tasks.md').write_text('- [ ] Task 2\n')

    (vault / 'keep.md').write_text('- [ ] Keep this\n')

    # Comma-separated with spaces
    result = run_cli('--filter', 'dir1, dir2', 'not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 1
    assert data['tasks'][0]['description'] == 'Keep this'


def test_filter_prefix_matching(tmp_path):
    """Test that filtering uses prefix matching, not exact matching."""
    vault = tmp_path

    (vault / 'project').mkdir()
    (vault / 'project' / 'tasks.md').write_text('- [ ] Project task\n')

    (vault / 'project-archived').mkdir()
    (vault / 'project-archived' / 'old.md').write_text('- [ ] Archived task\n')

    (vault / 'other.md').write_text('- [ ] Other task\n')

    # Filter 'project' should match both 'project/' and 'project-archived/'
    result = run_cli('--filter', 'project', 'not done', str(vault))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['count'] == 1
    assert data['tasks'][0]['description'] == 'Other task'


def test_filter_error_no_argument(tmp_path):
    """Test that --filter without argument shows error."""
    vault = tmp_path
    (vault / 'tasks.md').write_text('- [ ] Task\n')

    result = run_cli('--filter', 'not done', str(vault))
    assert result.returncode == 1
    assert 'Error' in result.stderr


def test_filter_error_empty_paths(tmp_path):
    """Test that --filter with only commas/whitespace shows error."""
    vault = tmp_path
    (vault / 'tasks.md').write_text('- [ ] Task\n')

    result = run_cli('--filter', '  ,  , ', 'not done', str(vault))
    assert result.returncode == 1
    assert 'Error' in result.stderr


def test_filter_with_raw_output(tmp_path):
    """Test that --filter works with --raw flag."""
    vault = tmp_path

    (vault / '.claude').mkdir()
    (vault / '.claude' / 'tasks.md').write_text('- [ ] Claude task\n')
    (vault / 'keep.md').write_text('- [ ] Keep task\n')

    result = run_cli('--raw', '--filter', '.claude', 'not done', str(vault))
    assert result.returncode == 0
    assert 'Keep task' in result.stdout
    assert 'Claude task' not in result.stdout


