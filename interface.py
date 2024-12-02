from disk_scanner import scan_directory, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage
from file_size import format_file_size


def print_tree(path, filters=None):
    """
    Prints the directory tree in a human-readable format using scan_directory.

    Args:
        path (str): The root directory path.
        filters (list): Optional list of filters to apply to the files.
    """
    try:
        tree_structure = scan_directory(path, filters=filters)
        print(tree_structure)
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def show_top_5_heavy_items(path, filters=None):
    """
    Show the top 5 largest files and directories in the given path.

    Args:
        path (str): The root directory path.
        filters (list): Optional list of filters to apply to the files.
    """
    try:
        top_items = get_top_5_heavy_items(path, filters)
        if top_items:
            print("\nTop 5 Largest Items:")
            for idx, item in enumerate(top_items, 1):
                print(f"{idx}. {item['name']} - {item['size']}")
        else:
            print("No items found.")
    except Exception as e:
        print(f"Error: {str(e)}")


def visualize_disk_usage_console(path, filters=None):
    """
    Simulate disk usage visualization in the console by summarizing directory sizes.

    Args:
        path (str): The root directory path.
        filters (list): Optional list of filters to apply to the files.
    """
    try:
        labels, sizes, formatted_sizes = visualize_disk_usage(path, filters)
        print("\nDisk Usage Summary:")
        for label, size, formatted_size in zip(labels, sizes, formatted_sizes):
            print(f"{label}: {formatted_size}")
    except Exception as e:
        print(f"Error: {str(e)}")


def main_menu():
    """
    Display the main menu and handle user input for the console interface.
    """
    while True:
        print("\n=== Disk Scanner ===")
        print("1. Scan directory and print tree")
        print("2. Show top 5 largest items")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            path = input("Enter directory path to scan: ").strip()
            filters_input = input("Enter file type filters (comma-separated, e.g., .txt,.py): ").strip()
            filters = [f.strip() for f in filters_input.split(",")] if filters_input else None
            print("\nDirectory tree structure:")
            print_tree(path, filters)
        elif choice == "2":
            path = input("Enter directory path to show top 5 largest items: ").strip()
            filters_input = input("Enter file type filters (comma-separated, e.g., .txt,.py): ").strip()
            filters = [f.strip() for f in filters_input.split(",")] if filters_input else None
            show_top_5_heavy_items(path, filters)
        elif choice == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main_menu()
