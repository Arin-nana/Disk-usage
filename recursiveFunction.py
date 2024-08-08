import os

from tqdm import tqdm

from GetSize import get_size
from GetSize import convert_size
from visualaser import visualize_memory_usage

def walk_through_directory_recursive(directory):
    total_size = 0
    file_count = 0
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    with tqdm(total=total_files, desc="Processing") as pbar:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                    pbar.update(1)
    return total_size, file_count

def list_files_with_size(directory, depth, file_extension=None, admin_required=False):
    files_with_size = []
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    with tqdm(total=total_files, desc="Processing") as pbar:
        def _recursive_list_files_with_size(directory, current_depth):
            if current_depth == 0:
                for item in os.listdir(directory):
                    full_path = os.path.join(directory, item)
                    if admin_required and not os.access(full_path, os.R_OK):
                        continue
                    if os.path.isfile(full_path):
                        if not file_extension or full_path.endswith(file_extension):
                            size = get_size(full_path, file_extension)
                            files_with_size.append((item, size))
                    else:
                        size = get_size(full_path, file_extension)
                        files_with_size.append((item, size))
                return

            try:
                for item in os.listdir(directory):
                    full_path = os.path.join(directory, item)
                    if admin_required and not os.access(full_path, os.R_OK):
                        continue
                    if os.path.isfile(full_path):
                        if not file_extension or full_path.endswith(file_extension):
                            size = get_size(full_path, file_extension)
                            files_with_size.append((item, size))
                    pbar.update(1)
                    if os.path.isdir(full_path):
                        _recursive_list_files_with_size(full_path, current_depth - 1)
            except PermissionError:
                print("Нет доступа к папке:", directory)

        _recursive_list_files_with_size(directory, depth)
    return files_with_size

def explore_directory_with_size(startDirection, count, file_extension=None, admin_required=False):
    total_size = 0
    if not count.isdigit():
        result = list_files_with_size(startDirection, 0, file_extension, admin_required)
    else:
        result = list_files_with_size(startDirection, int(count), file_extension, admin_required)
    for item in result:
        total_size += item[1]
        print(f"{item[0]} - {convert_size(item[1])}")
    visualize_memory_usage(result, total_size)
    print(f"Общий размер - {convert_size(total_size)}")