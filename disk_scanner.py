import os
import logging
from file_size import calculate_size, format_file_size
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def scan_directory(path, level=0, visited=None, filters=None):
    logging.debug(f"Scanning directory: {path} at level {level}")
    if not os.path.exists(path):
        logging.error(f"Path does not exist: {path}")
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    if visited is None:
        visited = set()

    resolved_path = os.path.realpath(path)
    if resolved_path in visited:
        logging.warning(f"Cycle detected, skipping: {resolved_path}")
        return f"{'    ' * level}[SYMLINK] {os.path.basename(path)} -> {os.readlink(path)}\n"

    visited.add(resolved_path)
    result = []
    try:
        items = sorted(os.listdir(path), key=lambda x: x.lower())
        with ThreadPoolExecutor() as executor:
            futures = []

            for item in items:
                item_path = os.path.join(path, item)
                if os.path.islink(item_path):
                    logging.debug(f"Found symlink: {item_path}")
                    if os.path.isdir(item_path):
                        futures.append(executor.submit(scan_directory, item_path, level + 1, visited, filters))
                    elif filters is None or any(item_path.endswith(f) for f in filters):
                        size = calculate_size(item_path)
                        formatted_size = format_file_size(size)
                        result.append(f"{'    ' * level}[SYMLINK] {item} - {formatted_size}\n")
                elif os.path.isdir(item_path):
                    futures.append(executor.submit(scan_directory, item_path, level + 1, visited, filters))
                elif filters is None or any(item_path.endswith(f) for f in filters):
                    size = calculate_size(item_path)
                    formatted_size = format_file_size(size)
                    result.append(f"{'    ' * level}{item} - {formatted_size}\n")

            for future in futures:
                try:
                    result.append(future.result())
                except Exception as e:
                    logging.error(f"Error processing item: {e}")
    except PermissionError as e:
        logging.warning(f"Permission denied: {path}. Exception: {e}")
        result.append(f"{'    ' * level}[ACCESS DENIED]\n")
    except FileNotFoundError:
        logging.warning(f"Path not found: {path}")

    return "".join(result)

def calculate_total_items(path):
    """Calculate total items in the directory tree for progress tracking."""
    total = 0
    try:
        for _, dirs, files in os.walk(path):
            total += len(dirs) + len(files)
    except Exception as e:
        logging.error(f"Error calculating total items: {e}")
    return total
def get_top_5_heavy_items(directory, filters=None):
    """
    Get the 5 largest files or directories in the specified directory with optional filters.
    """
    logging.info(f"Retrieving top 5 heaviest items in: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"'{directory}' is not a valid directory.")

    def apply_filters(item_path):
        if not filters:
            return True
        return any(item_path.endswith(ext.strip()) for ext in filters)

    items = []
    visited = set()

    for root, dirs, files in os.walk(directory):
        resolved_root = os.path.realpath(root)
        if resolved_root in visited:
            continue
        visited.add(resolved_root)

        for file in files:
            file_path = os.path.join(root, file)
            if not apply_filters(file_path):
                continue
            try:
                size = os.path.getsize(file_path)
                items.append({"name": file_path, "size": size})
            except FileNotFoundError:
                logging.warning(f"File not found: {file_path}")

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not apply_filters(dir_path):
                continue
            resolved_path = os.path.realpath(dir_path)
            if resolved_path in visited:
                continue
            try:
                size = sum(
                    os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path)
                    if os.path.isfile(os.path.join(dir_path, f))
                )
                items.append({"name": dir_path, "size": size})
            except FileNotFoundError:
                logging.warning(f"Directory not found: {dir_path}")

    items = sorted(items, key=lambda x: x["size"], reverse=True)[:5]
    logging.info("Top 5 heaviest items retrieved.")
    return [{"name": item["name"], "size": format_file_size(item["size"])} for item in items]
