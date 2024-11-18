import os
import logging
import matplotlib.pyplot as plt
from file_size import calculate_size, format_file_size

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def visualize_disk_usage(path):
    """
    Generate a visual representation of disk usage.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    labels = []
    sizes = []
    for root, dirs, files in os.walk(path):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            size = calculate_size(full_path)
            if size > 0:
                labels.append(name)
                sizes.append(size)

    if not sizes:
        raise ValueError("No data found for visualization.")

    return labels, sizes


def plot_disk_usage(labels, sizes):
    """
    Plot a pie chart of disk usage.
    """
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title("Disk Usage Visualization")
    plt.show()
