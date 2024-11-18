import os
import pytest
from disk_scanner import scan_directory
from file_size import calculate_size, format_file_size
from visualizer import visualize_disk_usage

# === TEST DATA SETUP ===
@pytest.fixture
def test_directory(tmp_path):
    """
    Fixture to create a temporary directory structure for testing.
    """
    # Create main test directory
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create files in the main directory
    (test_dir / "file1.txt").write_text("File 1 content")
    (test_dir / "file2.txt").write_text("File 2 content")
    (test_dir / "file3.log").write_text("Log content")

    # Create a subdirectory
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file4.txt").write_text("File 4 content")

    return test_dir


# === TESTS FOR disk_scanner.py ===

def test_scan_directory_invalid_path():
    """
    Test scanning an invalid directory path.
    """
    with pytest.raises(FileNotFoundError):
        scan_directory("invalid_path")


# === TESTS FOR file_size.py ===
def test_calculate_size_file(test_directory):
    """
    Test calculating the size of a single file.
    """
    file_path = test_directory / "file1.txt"
    size = calculate_size(str(file_path))
    assert size == os.path.getsize(file_path)


def test_calculate_size_directory(test_directory):
    """
    Test calculating the size of a directory.
    """
    size = calculate_size(str(test_directory))
    assert size > 0


def test_format_file_size():
    """
    Test formatting file sizes into readable strings.
    """
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1048576) == "1.0 MB"
    assert format_file_size(1073741824) == "1.0 GB"


# === TESTS FOR visualizer.py ===
def test_visualize_disk_usage_no_filter(test_directory):
    """
    Test visualizing disk usage without file extension filtering.
    """
    result = visualize_disk_usage(str(test_directory))
    assert "file1.txt" in result
    assert "subdir" in result  # Проверка на наличие поддиректории
    assert "file4.txt" in result  # Проверка на файлы внутри поддиректории



def test_visualize_disk_usage_with_filter(test_directory):
    """
    Test visualizing disk usage with file extension filtering.
    """
    result = visualize_disk_usage(str(test_directory), extension_filter=".txt")
    assert "file2.log" not in result
    assert "file1.txt" in result


def test_visualize_disk_usage_invalid_path():
    """
    Test visualizing disk usage for an invalid path.
    """
    result = visualize_disk_usage("invalid_path")
    assert "Error" in result


# === TESTS FOR interface ===
# Not directly testable due to input/output dependency.
# Would require mocking user input for proper testing.
