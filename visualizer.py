import os
import matplotlib.pyplot as plt
from file_size import calculate_size, format_file_size

def visualize_disk_usage(path, extension_filter=None):
    """
    Generate a visual representation of disk usage.

    :param path: Directory path to visualize.
    :param extension_filter: Optional file extension to filter files.
    :return: Tuple of labels and sizes for visualization.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    data = []
    labels = []

    for root, dirs, files in os.walk(path):
        for item in dirs + files:
            item_path = os.path.join(root, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                if extension_filter and not item.endswith(extension_filter):
                    continue
                size = calculate_size(item_path)
                data.append(size)
                labels.append(item)

    if not data:
        raise ValueError("No data found for visualization.")

    return labels, data


def plot_disk_usage(labels, sizes):
    """
    Plot a pie chart of disk usage.

    :param labels: Labels of files/directories.
    :param sizes: Corresponding sizes of files/directories.
    """
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    plt.title("Disk Usage Visualization")
    plt.show()
