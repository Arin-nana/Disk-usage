import unittest
from unittest.mock import patch, MagicMock
import os

import main
import recursiveFunction
import GetSize

class TestGetSize(unittest.TestCase):

    def setUp(self):
        self.test_file_path = 'test_file.txt'
        self.test_file_size = 100
        with open(self.test_file_path, 'w') as f:
            f.write('a' * self.test_file_size)

        self.test_dir_path = 'test_dir'
        os.mkdir(self.test_dir_path)
        self.test_file_path_in_dir = os.path.join(self.test_dir_path, 'test_file_in_dir.txt')
        with open(self.test_file_path_in_dir, 'w') as f:
            f.write('a' * self.test_file_size)

    def tearDown(self):
        os.remove(self.test_file_path)
        os.remove(self.test_file_path_in_dir)
        os.rmdir(self.test_dir_path)

    def test_get_size_file(self):
        self.assertEqual(GetSize.get_size(self.test_file_path), self.test_file_size)

    def test_get_size_file_with_extension(self):
        self.assertEqual(GetSize.get_size(self.test_file_path, '.txt'), self.test_file_size)

    def test_get_size_dir(self):
        self.assertEqual(GetSize.get_size(self.test_dir_path), self.test_file_size)

    def test_get_size_dir_with_extension(self):
        self.assertEqual(GetSize.get_size(self.test_dir_path, '.txt'), self.test_file_size)

    def test_get_size_non_existent_file(self):
        self.assertIsNone(GetSize.get_size('non_existent_file.txt'))

    def test_get_size_non_existent_dir(self):
        self.assertIsNone(GetSize.get_size('non_existent_dir'))

class TestConvertSize(unittest.TestCase):

    def test_convert_size_bytes(self):
        self.assertEqual(GetSize.convert_size(100), "100 bytes")

    def test_convert_size_kb(self):
        self.assertEqual(GetSize.convert_size(1024), "1.00 KB")

    def test_convert_size_mb(self):
        self.assertEqual(GetSize.convert_size(1024 * 1024), "1.00 MB")

    def test_convert_size_gb(self):
        self.assertEqual(GetSize.convert_size(1024 * 1024 * 1024), "1.00 GB")

    def test_convert_size_kb_boundary(self):
        self.assertEqual(GetSize.convert_size(1023), "1023 bytes")
        self.assertEqual(GetSize.convert_size(1024), "1.00 KB")

    def test_convert_size_mb_boundary(self):
        self.assertEqual(GetSize.convert_size(1024 * 1024 - 1), "1024.00 KB")
        self.assertEqual(GetSize.convert_size(1024 * 1024), "1.00 MB")

    def test_convert_size_gb_boundary(self):
        self.assertEqual(GetSize.convert_size(1024 * 1024 * 1024 - 1), "1024.00 MB")
        self.assertEqual(GetSize.convert_size(1024 * 1024 * 1024), "1.00 GB")

    def test_convert_size_invalid_input(self):
        with self.assertRaises(TypeError):
            GetSize.convert_size("invalid input")

class TestDirectoryFunctions(unittest.TestCase):

    def setUp(self):
        self.test_dir_path = 'test_dir'
        os.mkdir(self.test_dir_path)
        self.test_file_path = os.path.join(self.test_dir_path, 'test_file.txt')
        with open(self.test_file_path, 'w') as f:
            f.write('a' * 100)

    def tearDown(self):
        os.remove(self.test_file_path)
        os.rmdir(self.test_dir_path)

    def test_walk_through_directory_recursive(self):
        total_size, file_count = recursiveFunction.walk_through_directory_recursive(self.test_dir_path)
        self.assertEqual(total_size, 100)
        self.assertEqual(file_count, 1)

    def test_list_files_with_size(self):
        files_with_size = recursiveFunction.list_files_with_size(self.test_dir_path, 0)
        self.assertEqual(len(files_with_size), 1)
        self.assertEqual(files_with_size, [('test_file.txt', 100)])

    def test_list_files_with_size_with_extension(self):
        files_with_size = recursiveFunction.list_files_with_size(self.test_dir_path, 0, '.txt')
        self.assertEqual(len(files_with_size), 1)
        self.assertEqual(files_with_size, [('test_file.txt', 100)])

    def test_list_files_with_size_admin_required(self):
        with patch('os.access', return_value=False) as mock_access:
            files_with_size = recursiveFunction.list_files_with_size(self.test_dir_path, 0, admin_required=True)
            self.assertEqual(len(files_with_size), 0)
            mock_access.assert_called_once_with(self.test_file_path, os.R_OK)

    @patch('os.walk')
    @patch('os.listdir')
    @patch('os.path.join')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_list_files_with_size_permission_error(self, mock_access, mock_isfile, mock_join, mock_listdir, mock_walk):
        mock_walk.return_value = [('path', ['dir1', 'dir2'], ['file1.txt', 'file2.txt', 'file3.py'])]
        mock_listdir.return_value = ['file1.txt', 'file2.txt', 'file3.py']
        mock_join.return_value = 'path/file1.txt'
        mock_isfile.return_value = True
        mock_access.return_value = True
        mock_listdir.side_effect = PermissionError
        mock_get_size = MagicMock(return_value=100)
        with patch('GetSize.get_size', mock_get_size):
            result = recursiveFunction.list_files_with_size('directory', 1, 'txt')
            self.assertEqual(result, [])

    @patch('os.walk')
    @patch('os.access')
    def test_explore_directory_with_size(self, mock_access, mock_walk):
        mock_walk.return_value = [('path', ['dir1', 'dir2'], ['file1.txt', 'file2.txt', 'file3.py'])]
        mock_access.return_value = True
        mock_list_files_with_size = MagicMock(return_value=[('file1.txt', 100), ('file2.txt', 200), ('file3.py', 300)])
        with patch('recursiveFunction.list_files_with_size', mock_list_files_with_size):
            with patch('GetSize.convert_size', side_effect=lambda x: f'{x} bytes'):
                recursiveFunction.explore_directory_with_size('startDirection', '2', 'txt')
                mock_list_files_with_size.assert_called_once_with('startDirection', 2, 'txt', False)

class TestPrintInterface2(unittest.TestCase):

    def test_print_interface2(self):
        with patch('builtins.print') as mock_print:
            main.print_interface2()
            mock_print.assert_called()

class TestMain(unittest.TestCase):
    @patch('builtins.input', side_effect=['clear', 'exit'])
    def test_main_clear(self, mock_input):
        with patch('os.system') as mock_os_system:
            main.main()
            mock_os_system.assert_called_once_with('clear')

if __name__ == '__main__':
    unittest.main()