def visualize_disk_usage(path):
    """
    Generate data for visual representation of disk usage in the specified directory.

    Args:
        path (str): The directory path.

    Returns:
        list, list: Two lists containing labels and sizes of files and folders in the directory.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    labels = []
    sizes = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        size = calculate_size(item_path)
        if size > 0:  # Exclude empty items
            labels.append(item)
            sizes.append(size)

    if not sizes:
        raise ValueError("No data found for visualization.")
    
    return labels, sizes


def plot_disk_usage(labels, sizes):
    """
    Plot a pie chart of disk usage with labels displayed separately as a list.

    Args:
        labels (list): List of labels for files and folders.
        sizes (list): List of sizes corresponding to the labels.
    """
    # Calculate percentages for each item
    total_size = sum(sizes)
    percentages = [(size / total_size) * 100 for size in sizes]

    # Create a figure with two subplots: pie chart and list of labels
    fig, (ax_pie, ax_list) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [3, 2]})

    # Plot the pie chart
    ax_pie.pie(
        sizes, startangle=140, wedgeprops=dict(width=0.4), autopct=None, colors=plt.cm.tab20.colors
    )
    ax_pie.set_title("Disk Usage Visualization", fontsize=14)

    # Create a text list with labels and percentages
    label_texts = [f"{label}: {percent:.1f}% ({format_file_size(size)})" for label, percent, size in zip(labels, percentages, sizes)]
    ax_list.axis('off')  # Remove axes
    ax_list.text(0, 1, "\n".join(label_texts), fontsize=10, verticalalignment='top', family='monospace')

    plt.tight_layout()
    plt.show()
