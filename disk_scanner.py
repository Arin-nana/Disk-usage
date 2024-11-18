import os
import logging
from file_size import calculate_size, format_file_size

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def scan_directory(path, level=0):
    """
    Scans a directory recursively and returns a formatted string with nested files and folders.

    Args:
        path (str): The path to the directory to scan.
        level (int): The current depth of recursion for formatting.

    Returns:
        str: A formatted string representing the directory structure.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    result = []
    indent = "    " * level  # Indentation based on depth level
    result.append(f"{indent}> {os.path.basename(path)}\n")

    for item in sorted(os.listdir(path), key=lambda x: x.lower()):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            result.append(f"{indent}    [DIR] {item}\n")
            result.append(scan_directory(item_path, level + 1))  # Recursive call for subdirectories
        else:
            size = calculate_size(item_path)
            formatted_size = format_file_size(size)
            result.append(f"{indent}    {item} - {formatted_size}\n")

    return "".join(result)


def get_top_5_heavy_items(directory):
    """
    Get the 5 largest files or directories in the specified directory.
    """
    logging.info(f"Retrieving top 5 heaviest items in: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"'{directory}' is not a valid directory.")

    items = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                items.append({"name": file_path, "size": size})
            except FileNotFoundError:
                logging.warning(f"File not found: {file_path}")

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
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
