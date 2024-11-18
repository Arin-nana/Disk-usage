import os

def format_file_size(bytes_size):
    """Format bytes into a human-readable string."""
    if bytes_size >= 1024 ** 3:
        return f"{bytes_size / 1024 ** 3:.1f} GB"
    elif bytes_size >= 1024 ** 2:
        return f"{bytes_size / 1024 ** 2:.1f} MB"
    elif bytes_size >= 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size} bytes"

def calculate_size(path, extension_filter=None):
    """Calculate total size of files and directories."""
    if os.path.isfile(path) and (not extension_filter or path.endswith(extension_filter)):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for file in filenames:
                full_path = os.path.join(dirpath, file)
                if not extension_filter or full_path.endswith(extension_filter):
                    total += os.path.getsize(full_path)
        return total
    return None
