import pytest
import os
from unittest.mock import patch
from disk_scanner import scan_directory, get_top_5_heavy_items
from file_size import format_file_size, calculate_size
from visualizer import visualize_disk_usage
import time
from unittest.mock import MagicMock


@pytest.fixture
def test_directory_structure(tmp_path):
    os.symlink(tmp_path / "symlink_dir", tmp_path / "symlink")
    return tmp_path

def test_scan_directory_with_symlink(test_directory_structure):
    path = str(test_directory_structure)
    result = scan_directory(path)
    assert "[SYMLINK]" in result


@pytest.fixture
def test_directory_with_symlink(tmp_path):
    """
    Create a temporary directory structure with a symbolic link.
    """
    # Create directories and files
    dir_a = tmp_path / "dir_a"
    dir_a.mkdir()
    file_a = dir_a / "file_a.txt"
    file_a.write_text("This is file A.")

    dir_b = tmp_path / "dir_b"
    dir_b.mkdir()
    file_b = dir_b / "file_b.txt"
    file_b.write_text("This is file B.")

    # Create a symlink
    symlink = tmp_path / "dir_symlink"
    os.symlink(dir_a, symlink)

    return tmp_path

def test_scan_directory_with_symlink_filter(test_directory_with_symlink):
    """
    Test scanning a directory with a symlink and filters enabled.
    """
    path = str(test_directory_with_symlink)
    filters = [".txt"]

    # Mocking ThreadPoolExecutor to observe behavior
    original_executor = scan_directory.__globals__["ThreadPoolExecutor"]
    mock_executor = MagicMock(wraps=original_executor)

    scan_directory.__globals__["ThreadPoolExecutor"] = mock_executor
    result = scan_directory(path, filters=filters)

    # Ensure symlinks are handled correctly
    assert "[SYMLINK]" in result
    assert "file_a.txt" in result
    assert "file_b.txt" in result

    # Ensure ThreadPoolExecutor is called
    assert mock_executor.call_count > 0

    # Cleanup
    scan_directory.__globals__["ThreadPoolExecutor"] = original_executor

