import os
from file_size import calculate_size, format_file_size

def scan_directory(directory, extension_filter=None):
    """
    Scans the directory and returns a list of files and directories with sizes.
    """
    results = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if extension_filter and not name.endswith(extension_filter):
                continue
            path = os.path.join(root, name)
            size = os.path.getsize(path)
            results.append({"type": "File", "name": path, "size": f"{size} bytes"})

        for name in dirs:
            path = os.path.join(root, name)
            results.append({"type": "Directory", "name": path, "size": "N/A"})
    return results

def get_subdirectories(path):
    """
    Retrieve a list of subdirectories in the given path.

    :param path: Path to scan for subdirectories.
    :return: List of subdirectory paths.
    """
    return [os.path.join(path, name) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
