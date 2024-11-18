import os
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from file_size import calculate_size, format_file_size

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def visualize_disk_usage(path):
    """
    Generate a visual representation of disk usage with a pie chart.
    Includes a legend with file/folder names and percentages.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    # Collect sizes of top-level items only
    labels = []
    sizes = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.islink(item_path):  # Skip symbolic links
            continue
        size = calculate_size(item_path)
        if size > 0:
            labels.append(item)
            sizes.append(size)

    if not sizes:
        raise ValueError("No data found for visualization.")

    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts = ax.pie(sizes, startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures a circular pie chart
    ax.set_title("Disk Usage Visualization")

    # Create legend with file names, percentages, and matching colors
    total_size = sum(sizes)
    percentages = [f"{(size / total_size) * 100:.1f}%" for size in sizes]
    legend_items = [f"{label} ({percentage})" for label, percentage in zip(labels, percentages)]
    colors = [w.get_facecolor() for w in wedges]

    # Plot legend separately
    plt.figure(figsize=(6, len(labels) * 0.5))
    for i, (label, color) in enumerate(zip(legend_items, colors)):
        plt.plot([], [], marker="o", markersize=10, color=color, label=label)
    plt.legend(loc="center left", bbox_to_anchor=(0, 0.5), title="Files and Folders")
    plt.axis("off")  # Hide the axis for legend

    # Show both figures
    plt.show()



def plot_disk_usage(labels, sizes, formatted_sizes):
    """
    Plot a pie chart of disk usage with a legend for filenames and sizes.

    Args:
        labels (list): List of file and folder names.
        sizes (list): Corresponding sizes in bytes.
        formatted_sizes (list): Human-readable size strings.
    """
    # Create a color palette
    colors = plt.cm.tab10.colors[:len(labels)]

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _, _ = ax.pie(
        sizes,
        colors=colors,
        startangle=140,
        wedgeprops={'linewidth': 0.5, 'edgecolor': 'black'}
    )

    # Add a legend with file/folder names, sizes, and corresponding colors
    legend_elements = [
        Patch(facecolor=colors[i], edgecolor='black', label=f"{labels[i]}: {formatted_sizes[i]} ({sizes[i] / sum(sizes):.1%})")
        for i in range(len(labels))
    ]
    ax.legend(
        handles=legend_elements,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=9,
        title="Files and Folders"
    )

    # Remove text from the chart itself
    plt.title("Disk Usage Visualization (Current Directory)")
    plt.tight_layout()
    plt.show()