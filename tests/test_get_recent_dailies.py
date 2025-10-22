"""Quick test for get_recent_dailies function."""

from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from mcp_vault.implementation import get_recent_dailies


def test_get_recent_dailies():
    """Test the get_recent_dailies function."""

    # Create a temporary vault directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Create the directories
        inbox_dir = vault_path / "00_Inbox"
        dailies_dir = vault_path / "06_Metadata" / "Dailies"
        inbox_dir.mkdir(parents=True)
        dailies_dir.mkdir(parents=True)

        # Create today's daily note
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = inbox_dir / f"{today}.md"
        today_file.write_text(f"# Daily Note for {today}\n\nToday's content")

        # Create some archived daily notes
        archived_dates = ["2025-10-20", "2025-10-19", "2025-10-18", "2025-10-17"]
        for date in archived_dates:
            daily_file = dailies_dir / f"{date}.md"
            daily_file.write_text(f"# Daily Note for {date}\n\nArchived content")

        # Test 1: Get recent dailies without content (default limit=7)
        print("Test 1: Get paths only")
        result = get_recent_dailies(vault_path, limit=3, include_content=False)
        print(result)
        print()

        # Check that we get the expected number of files
        lines = result.strip().split('\n')
        assert len(lines) == 3, f"Expected 3 files, got {len(lines)}"

        # Check that today's note is first
        assert today in lines[0], f"Today's note should be first, got {lines[0]}"

        # Test 2: Get recent dailies with content
        print("Test 2: Get with content")
        result = get_recent_dailies(vault_path, limit=2, include_content=True)
        print(result[:200] + "...")
        print()

        # Check that content is included
        assert "===" in result, "Content should include file headers"
        assert "Today's content" in result or "Archived content" in result, "Content should be included"

        # Test 3: Verify correct ordering and limiting
        print("Test 3: Verify ordering (today first, then most recent) and limiting")
        result = get_recent_dailies(vault_path, limit=4, include_content=False)
        print(result)
        print()

        lines = result.strip().split('\n')
        # Should get: today + 3 most recent archived notes = 4 total
        assert len(lines) == 4, f"Expected 4 files (limit=4), got {len(lines)}"

        # Verify order: today first
        assert today in lines[0], f"Today's note ({today}) should be first, got {lines[0]}"

        # Verify order: most recent archived notes follow in descending order
        assert "2025-10-20" in lines[1], f"Second should be 2025-10-20, got {lines[1]}"
        assert "2025-10-19" in lines[2], f"Third should be 2025-10-19, got {lines[2]}"
        assert "2025-10-18" in lines[3], f"Fourth should be 2025-10-18, got {lines[3]}"

        # 2025-10-17 should NOT be in the results (exceeded limit)
        result_text = '\n'.join(lines)
        assert "2025-10-17" not in result_text, "2025-10-17 should not be in results (exceeded limit)"

        print("  ✓ Today's note is first")
        print("  ✓ Archived notes are in descending chronological order")
        print("  ✓ Limit is correctly applied")
        print()

        # Test 4: Test with only archived notes (no today's note)
        print("Test 4: Without today's note")
        today_file.unlink()  # Remove today's note
        result = get_recent_dailies(vault_path, limit=2, include_content=False)
        print(result)
        print()

        lines = result.strip().split('\n')
        # Note: The function reserves one spot for today's note even if it doesn't exist
        # So with limit=2, we get 1 archived note (limit - 1)
        assert len(lines) == 1, f"Expected 1 file (limit-1 when today's note absent), got {len(lines)}"
        assert "2025-10-20" in lines[0], "Most recent archived note should be first"

        print("All tests passed!")


if __name__ == "__main__":
    test_get_recent_dailies()
