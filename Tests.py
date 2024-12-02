import pytest
import os
import tempfile
import shutil
from disk_scanner import scan_directory, get_top_5_heavy_items
from file_size import format_file_size, calculate_size
from visualizer import visualize_disk_usage
from unittest.mock import patch, MagicMock
from tkinter import Tk
from disk_scanner_gui import DiskScannerGUI

@pytest.fixture
def temp_dir():
    """Фикстура для создания временной директории."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)


@pytest.fixture
def temp_file():
    """Фикстура для создания временного файла."""
    file = tempfile.NamedTemporaryFile(delete=False)
    yield file.name
    os.remove(file.name)


def test_scan_directory_nonexistent():
    with pytest.raises(FileNotFoundError):
        scan_directory('nonexistent_path')


def test_get_top_5_heavy_items(temp_dir):
    file_sizes = [100, 200, 300, 400, 500, 600]
    for i, size in enumerate(file_sizes):
        with open(os.path.join(temp_dir, f'file{i}.txt'), 'wb') as f:
            f.write(b'0' * size)

    top_items = get_top_5_heavy_items(temp_dir)
    expected_files = [os.path.join(temp_dir, f'file{5 - i}.txt') for i in range(5)]
    returned_files = [item['name'] for item in top_items]
    assert returned_files == expected_files


def test_get_top_5_heavy_items_not_directory():
    with pytest.raises(NotADirectoryError):
        get_top_5_heavy_items('not_a_directory')


def test_symbolic_links_in_scan(temp_dir):
    # Создаем символическую ссылку
    target_file = os.path.join(temp_dir, 'target.txt')
    with open(target_file, 'w') as f:
        f.write("Target file content")

    symlink_path = os.path.join(temp_dir, 'symlink.txt')
    os.symlink(target_file, symlink_path)

    # Проверяем, что символическая ссылка корректно обрабатывается
    result = scan_directory(temp_dir)

    # Ожидаемая информация о символической ссылке
    symlink_info = f"[SYMLINK] symlink.txt - 19 bytes\n"
    target_info = f"target.txt - 19 bytes\n"

    assert symlink_info in result, f"Expected symbolic link info '{symlink_info}' in result:\n{result}"
    assert target_info in result, f"Expected target file info '{target_info}' in result:\n{result}"


def test_format_file_size():
    assert format_file_size(500) == '500 bytes'
    assert format_file_size(1024) == '1.0 KB'
    assert format_file_size(1024 ** 2) == '1.0 MB'
    assert format_file_size(1024 ** 3) == '1.0 GB'

def test_calculate_size_directory(temp_dir):
    with open(os.path.join(temp_dir, 'file1.txt'), 'wb') as f:
        f.write(b'0' * 100)
    with open(os.path.join(temp_dir, 'file2.txt'), 'wb') as f:
        f.write(b'0' * 200)
    assert calculate_size(temp_dir) == 300


def test_calculate_size_nonexistent():
    assert calculate_size('nonexistent_path') == 0


def test_visualize_disk_usage_empty(temp_dir):
    with pytest.raises(ValueError):
        visualize_disk_usage(temp_dir)


def test_visualize_disk_usage_with_data(temp_dir):
    with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
        f.write('File 1 content')
    with open(os.path.join(temp_dir, 'file2.txt'), 'w') as f:
        f.write('File 2 content')
    try:
        visualize_disk_usage(temp_dir)  # Ожидается, что ошибок не будет
    except Exception as e:
        pytest.fail(f"visualize_disk_usage raised an exception {e}")


def test_filter_application_in_gui(temp_dir):
    from disk_scanner_gui import DiskScannerGUI

    app = DiskScannerGUI()
    app.filters_enabled.set(True)
    app.filters.set('.txt')

    with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
        f.write("Test content")
    with open(os.path.join(temp_dir, 'file2.log'), 'w') as f:
        f.write("Test log content")

    count = app.count_filtered_items(temp_dir)
    assert count == 1  # Учитывается только файл с расширением .txt


def test_format_file_size():
    assert format_file_size(0) == "0 bytes"
    assert format_file_size(512) == "512 bytes"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1536) == "1.5 KB"
    assert format_file_size(1024 ** 2) == "1.0 MB"
    assert format_file_size(1024 ** 3) == "1.0 GB"

@pytest.fixture
def temp_dir_with_files(tmp_path):
    # Создаем временную директорию с файлами
    file1 = tmp_path / "file1.txt"
    file1.write_text("12345")  # 5 bytes

    file2 = tmp_path / "file2.txt"
    file2.write_text("1234567890")  # 10 bytes

    subdir = tmp_path / "subdir"
    subdir.mkdir()

    file3 = subdir / "file3.txt"
    file3.write_text("123456")  # 6 bytes

    return tmp_path

def test_calculate_size_file(temp_dir_with_files):
    # Проверяем размер отдельного файла
    file1 = temp_dir_with_files / "file1.txt"
    assert calculate_size(file1) == 5

def test_calculate_size_directory(temp_dir_with_files):
    # Проверяем размер директории
    assert calculate_size(temp_dir_with_files) == 21  # 5 + 10 + 6

def test_calculate_size_empty_directory(tmp_path):
    # Проверяем размер пустой директории
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    assert calculate_size(empty_dir) == 0

def test_calculate_size_missing_file():
    # Проверяем поведение для несуществующего пути
    missing_file = "nonexistent.txt"
    assert calculate_size(missing_file) == 0

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


@pytest.fixture
def app():
    """Фикстура для создания экземпляра GUI."""
    root = Tk()
    gui = DiskScannerGUI()
    yield gui
    gui.destroy()
    root.destroy()

def test_initial_state(app):
    """Тест начального состояния GUI."""
    assert app.title() == "Disk Scanner with Filters"
    assert not app.filters_enabled.get()
    assert app.filters.get() == ""
    assert app.total_items == 0

def test_apply_filters_disabled(app):
    """Тест фильтров, если они отключены."""
    file_path = "example.txt"
    assert app._apply_filters(file_path)

def test_apply_filters_enabled(app):
    """Тест работы фильтров, если они включены."""
    app.filters_enabled.set(True)
    app.filters.set(".txt,.py")
    assert app._apply_filters("example.txt")
    assert not app._apply_filters("example.jpg")

@patch("tkinter.messagebox.showerror")
def test_scan_with_invalid_directory(mock_showerror, app):
    """Тест обработки некорректной директории при сканировании."""
    app.path_entry.insert(0, "invalid_path")
    app._scan_and_display_tree()
    mock_showerror.assert_called_once_with("Error", "'invalid_path' is not a valid directory.")

@patch("os.path.isdir", return_value=True)
@patch("disk_scanner_gui.DiskScannerGUI.count_filtered_items", return_value=10)
@patch("threading.Thread.start", MagicMock())
def test_scan_and_display_tree(mock_isdir, mock_count_filtered_items, app):
    """Тест вызова сканирования директории."""
    app.path_entry.insert(0, "valid_directory")
    app._scan_and_display_tree()
    assert app.total_items == 10
    mock_count_filtered_items.assert_called_once_with("valid_directory")


