import os
from disk_scanner import scan_directory
from visualizer import visualize_disk_usage

def main_menu():
    """
    Display the main menu and handle user input for disk scanning.
    """
    while True:
        print("\n=== Disk Scanner ===")
        print("1. Scan a directory")
        print("2. Visualize disk usage")
        print("3. Exit")

        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            scan_directory_menu()
        elif choice == "2":
            visualize_disk_usage_menu()
        elif choice == "3":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def scan_directory_menu():
    """
    Menu for scanning a directory and displaying its contents.
    """
    path = input("Enter the path to the directory: ").strip()
    extension = input("Enter a file extension to filter (or press Enter to skip): ").strip() or None

    try:
        contents = scan_directory(path, extension_filter=extension)
        if not contents:
            print(f"No files or directories found in '{path}'.")
        else:
            print("\nContents of the directory:")
            for item in contents:
                print(f"{item['type']}: {item['name']} ({item['size']})")
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")

def visualize_disk_usage_menu():
    """
    Menu for visualizing disk usage of a directory.
    """
    path = input("Enter the path to visualize: ").strip()
    extension = input("Enter a file extension to filter (or press Enter to skip): ").strip() or None

    result = visualize_disk_usage(path, extension_filter=extension)
    print("\n" + result)

if __name__ == "__main__":
    main_menu()
