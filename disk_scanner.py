import os
import logging
from file_size import calculate_size, format_file_size

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def scan_directory(path, level=0, visited=None):
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
        for item in sorted(os.listdir(path), key=lambda x: x.lower()):
            item_path = os.path.join(path, item)
            logging.debug(f"Processing item: {item_path}")

            if os.path.islink(item_path):
                logging.debug(f"Found symlink: {item_path}")
                # Handle symlinks...

            elif os.path.isdir(item_path):
                logging.debug(f"Entering directory: {item_path}")
                # Handle directories...
                result.append(scan_directory(item_path, level + 1, visited))

            else:
                size = calculate_size(item_path)
                formatted_size = format_file_size(size)
                logging.debug(f"File size of {item_path}: {formatted_size}")
                result.append(f"{'    ' * level}{item} - {formatted_size}\n")
    except PermissionError as e:
        logging.warning(f"Permission denied: {path}. Exception: {e}")
        result.append(f"{'    ' * level}[ACCESS DENIED]\n")

    return "".join(result)

# Similar logging improvements can be added to `get_top_5_heavy_items`.


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
