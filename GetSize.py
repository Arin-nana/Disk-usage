import os

def convert_size(size_bytes):
    if size_bytes >= 1024 * 1024 * 1024:
        size = size_bytes / (1024 * 1024 * 1024)
        return "%.2f GB" % size
    elif size_bytes >= 1024 * 1024:
        size = size_bytes / (1024 * 1024)
        return "%.2f MB" % size
    elif size_bytes >= 1024:
        size = size_bytes / 1024
        return "%.2f KB" % size
    else:
        return "%d bytes" % size_bytes

def get_size(file_path, file_extension=None):
    if os.path.isfile(file_path) and (not file_extension or file_path.endswith(file_extension)):
        return os.path.getsize(file_path)

    elif os.path.isdir(file_path):
        total_size = 0
        for dirpath, _, filenames in os.walk(file_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if not file_extension or filepath.endswith(file_extension):
                    total_size += os.path.getsize(filepath)
        return total_size