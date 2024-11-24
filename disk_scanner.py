
import os
import logging
from file_size import calculate_size, format_file_size

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def scan_directory(path, level=0, visited=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    if visited is None:
        visited = set()

    resolved_path = os.path.realpath(path)  # Resolve symbolic links
    if resolved_path in visited:
        return f"{'    ' * level}[SYMLINK] {os.path.basename(path)} -> {os.readlink(path)}\n"

    visited.add(resolved_path)

    result = []
    indent = "    " * level  # Indentation based on depth level
    result.append(f"{indent}> {os.path.basename(path)}\n")

    for item in sorted(os.listdir(path), key=lambda x: x.lower()):
        item_path = os.path.join(path, item)
        if os.path.islink(item_path):  # Handle symbolic links
            link_target = os.readlink(item_path)
            resolved_target = os.path.realpath(item_path)
            if resolved_target not in visited:
                if os.path.isdir(resolved_target):
                    result.append(f"{indent}    [SYMLINK DIR] {item} -> {link_target}\n")
                    result.append(scan_directory(resolved_target, level + 1, visited))  # Recurse
                else:
                    size = calculate_size(resolved_target)
                    formatted_size = format_file_size(size)
                    result.append(f"{indent}    [SYMLINK FILE] {item} -> {link_target} - {formatted_size}\n")
            else:
                result.append(f"{indent}    [SYMLINK] {item} -> {link_target}\n")
        elif os.path.isdir(item_path):
            result.append(f"{indent}    [DIR] {item}\n")
            result.append(scan_directory(item_path, level + 1, visited))  # Recurse
        else:
            size = calculate_size(item_path)
            formatted_size = format_file_size(size)
            result.append(f"{indent}    {item} - {formatted_size}\n")

    return "".join(result)



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
    for root, dirs, files in os.walk(directory):
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
