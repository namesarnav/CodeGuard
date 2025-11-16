"""Integration tests for scanner."""

import pytest

from app.scanner.scanner import CodeScanner


@pytest.mark.asyncio
async def test_scan_local_directory(tmp_path):
    """Test scanning a local directory."""
    # Create a test file
    test_file = tmp_path / "test.py"
    test_file.write_text('def insecure_function(password):\n    return password\n')

    scanner = CodeScanner()
    result = await scanner.scan(repository_path=str(tmp_path))

    assert result.scan_id is not None
    assert result.status.value in ["completed", "failed"]
    assert result.total_files >= 1

