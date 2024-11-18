from disk_scanner import scan_directory, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage


def print_tree(path):
    """
    Prints the directory tree in a human-readable format using scan_directory.

    Args:
        path (str): The root directory path.
    """
    try:
        tree_structure = scan_directory(path)
        print(tree_structure)
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def main_menu():
    """
    Display the main menu and handle user input.
    """
    while True:
        print("\n=== Disk Scanner ===")
        print("1. Scan directory and print tree")
        print("2. Visualize disk usage")
        print("3. Show top 5 largest items")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            path = input("Enter directory path to scan: ").strip()
            print("\nDirectory tree structure:")
            print_tree(path)
        elif choice == "2":
            path = input("Enter directory path to visualize: ").strip()
            try:
                labels, sizes = visualize_disk_usage(path)
                plot_disk_usage(labels, sizes)
            except FileNotFoundError as e:
                print(f"Error: {str(e)}")
            except ValueError as e:
                print(f"Error: {str(e)}")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
        elif choice == "3":
            path = input("Enter directory path: ").strip()
            try:
                top_items = get_top_5_heavy_items(path)
                print("\nTop 5 largest items:")
                for item in top_items:
                    print(f"{item['name']}: {item['size']}")
            except FileNotFoundError as e:
                print(f"Error: {str(e)}")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
