<<<<<<< Updated upstream
# test_disk_scanner.py

=======
>>>>>>> Stashed changes
import unittest
import tempfile
import os
import shutil
from disk_scanner import scan_directory, get_top_5_heavy_items
from file_size import format_file_size, calculate_size
from visualizer import visualize_disk_usage

<<<<<<< Updated upstream
class TestDiskScanner(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after test
        shutil.rmtree(self.test_dir)

=======

class TestDiskScanner(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after test
        shutil.rmtree(self.test_dir)

>>>>>>> Stashed changes
    def test_scan_directory_nonexistent(self):
        # Test scanning a non-existent directory
        with self.assertRaises(FileNotFoundError):
            scan_directory('nonexistent_path')

    def test_scan_directory_empty(self):
        # Test scanning an empty directory
        output = scan_directory(self.test_dir)
        expected_output = f"> {os.path.basename(self.test_dir)}\n"
        self.assertEqual(output, expected_output)

    def test_scan_directory_with_files(self):
        # Create files and directories
        os.mkdir(os.path.join(self.test_dir, 'subdir'))
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('Test file 1')
        with open(os.path.join(self.test_dir, 'subdir', 'file2.txt'), 'w') as f:
            f.write('Test file 2')

        output = scan_directory(self.test_dir)
        self.assertIn('file1.txt -', output)
        self.assertIn('[DIR] subdir', output)
        self.assertIn('file2.txt -', output)
<<<<<<< Updated upstream


    def test_get_top_5_heavy_items(self):
        # Create files of different sizes
        file_sizes = [100, 200, 300, 400, 500, 600]
        for i, size in enumerate(file_sizes):
            with open(os.path.join(self.test_dir, f'file{i}.txt'), 'wb') as f:
                f.write(b'0' * size)
        top_items = get_top_5_heavy_items(self.test_dir)
        # Should return top 5 largest files
        expected_files = [os.path.join(self.test_dir, f'file{5 - i}.txt') for i in range(5)]
        returned_files = [item['name'] for item in top_items]
        self.assertEqual(returned_files, expected_files)

    def test_get_top_5_heavy_items_not_directory(self):
        # Test passing a non-directory path
        with self.assertRaises(NotADirectoryError):
            get_top_5_heavy_items('not_a_directory')
=======

    def test_scan_directory_with_symlinks(self):
        # Create files
        target_file = os.path.join(self.test_dir, 'file1.txt')
        with open(target_file, 'w') as f:
            f.write('Test file 1')

        symlink_path = os.path.join(self.test_dir, 'symlink_to_file1.txt')

        try:
            os.symlink(target_file, symlink_path)
        except (OSError, NotImplementedError) as e:
            # Skip the test if symlink creation is not permitted
            self.skipTest(f"Symlink creation not permitted: {e}")

        output = scan_directory(self.test_dir)
        self.assertIn('[SYMLINK FILE] symlink_to_file1.txt ->', output)

    def test_get_top_5_heavy_items(self):
        # Create files of different sizes
        file_sizes = [100, 200, 300, 400, 500, 600]
        for i, size in enumerate(file_sizes):
            with open(os.path.join(self.test_dir, f'file{i}.txt'), 'wb') as f:
                f.write(b'0' * size)
        top_items = get_top_5_heavy_items(self.test_dir)
        # Should return top 5 largest files
        expected_files = [os.path.join(self.test_dir, f'file{5 - i}.txt') for i in range(5)]
        returned_files = [item['name'] for item in top_items]
        self.assertEqual(returned_files, expected_files)

    def test_get_top_5_heavy_items_not_directory(self):
        # Test passing a non-directory path
        with self.assertRaises(NotADirectoryError):
            get_top_5_heavy_items('not_a_directory')


class TestFileSize(unittest.TestCase):

    def test_format_file_size(self):
        # Test formatting of various file sizes
        self.assertEqual(format_file_size(500), '500 bytes')
        self.assertEqual(format_file_size(1024), '1.0 KB')
        self.assertEqual(format_file_size(1024 ** 2), '1.0 MB')
        self.assertEqual(format_file_size(1024 ** 3), '1.0 GB')

    def test_calculate_size_file(self):
        # Test size calculation of a single file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'0' * 100)
            tmp_file_name = tmp_file.name
        size = calculate_size(tmp_file_name)
        self.assertEqual(size, 100)
        os.remove(tmp_file_name)

    def test_calculate_size_directory(self):
        # Test size calculation of a directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, 'file1.txt'), 'wb') as f:
                f.write(b'0' * 100)
            with open(os.path.join(tmp_dir, 'file2.txt'), 'wb') as f:
                f.write(b'0' * 200)
            size = calculate_size(tmp_dir)
            self.assertEqual(size, 300)

    def test_calculate_size_nonexistent(self):
        # Test size calculation of a non-existent path
        size = calculate_size('nonexistent_path')
        self.assertEqual(size, 0)
>>>>>>> Stashed changes

class TestFileSize(unittest.TestCase):

<<<<<<< Updated upstream
    def test_format_file_size(self):
        # Test formatting of various file sizes
        self.assertEqual(format_file_size(500), '500 bytes')
        self.assertEqual(format_file_size(1024), '1.0 KB')
        self.assertEqual(format_file_size(1024 ** 2), '1.0 MB')
        self.assertEqual(format_file_size(1024 ** 3), '1.0 GB')
=======
class TestVisualizer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after test
        shutil.rmtree(self.test_dir)

    def test_visualize_disk_usage_empty(self):
        # Test visualization with an empty directory
        with self.assertRaises(ValueError):
            visualize_disk_usage(self.test_dir)

    def test_visualize_disk_usage_nonexistent(self):
        # Test visualization with a non-existent path
        with self.assertRaises(FileNotFoundError):
            visualize_disk_usage('nonexistent_path')

    def test_visualize_disk_usage(self):
        # Create files for visualization
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('Test file 1')
        with open(os.path.join(self.test_dir, 'file2.txt'), 'w') as f:
            f.write('Test file 2')

        # Test that the visualization runs without exceptions
        try:
            visualize_disk_usage(self.test_dir)
        except Exception as e:
            self.fail(f"visualize_disk_usage raised an exception {e}")
>>>>>>> Stashed changes

    def test_calculate_size_file(self):
        # Test size calculation of a single file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'0' * 100)
            tmp_file_name = tmp_file.name
        size = calculate_size(tmp_file_name)
        self.assertEqual(size, 100)
        os.remove(tmp_file_name)

<<<<<<< Updated upstream
    def test_calculate_size_directory(self):
        # Test size calculation of a directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, 'file1.txt'), 'wb') as f:
                f.write(b'0' * 100)
            with open(os.path.join(tmp_dir, 'file2.txt'), 'wb') as f:
                f.write(b'0' * 200)
            size = calculate_size(tmp_dir)
            self.assertEqual(size, 300)

    def test_calculate_size_nonexistent(self):
        # Test size calculation of a non-existent path
        size = calculate_size('nonexistent_path')
        self.assertEqual(size, 0)

class TestVisualizer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after test
        shutil.rmtree(self.test_dir)

    def test_visualize_disk_usage_empty(self):
        # Test visualization with an empty directory
        with self.assertRaises(ValueError):
            visualize_disk_usage(self.test_dir)

    def test_visualize_disk_usage_nonexistent(self):
        # Test visualization with a non-existent path
        with self.assertRaises(FileNotFoundError):
            visualize_disk_usage('nonexistent_path')

    def test_visualize_disk_usage(self):
        # Create files for visualization
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('Test file 1')
        with open(os.path.join(self.test_dir, 'file2.txt'), 'w') as f:
            f.write('Test file 2')

        # Test that the visualization runs without exceptions
        try:
            visualize_disk_usage(self.test_dir)
        except Exception as e:
            self.fail(f"visualize_disk_usage raised an exception {e}")

=======
>>>>>>> Stashed changes
if __name__ == '__main__':
    unittest.main()
