import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from disk_scanner import scan_directory, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage
from file_size import format_file_size, calculate_size


class DiskScannerGUI(tk.Tk):
    """
    GUI application for scanning and visualizing disk usage.
    """

    def __init__(self):
        super().__init__()
        self.title("Disk Scanner with Tree View")
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and packs all widgets for the application.
        """
        tk.Label(self, text="Enter directory path:").pack(pady=5)

        # Path input and browse button
        frame = tk.Frame(self)
        frame.pack(pady=5)
        self.path_entry = tk.Entry(frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse", command=self._browse_directory).pack(side=tk.LEFT)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="indeterminate", length=300)
        self.progress_bar.pack(pady=10)

        # Action buttons
        tk.Button(self, text="Scan and Display Tree", command=self._scan_and_display_tree).pack(pady=5)
        tk.Button(self, text="Visualize Disk Usage", command=self._visualize_disk_usage).pack(pady=5)
        tk.Button(self, text="Show Top 5 Largest Items", command=self._show_top_5_heavy_items).pack(pady=5)

        # TreeView for displaying directory structure
        self.tree = ttk.Treeview(self, columns=("size"), displaycolumns=("size"))
        self.tree.heading("#0", text="Directory Structure", anchor="w")
        self.tree.heading("size", text="Size", anchor="w")
        self.tree.column("size", anchor="w", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def _browse_directory(self):
        """
        Opens a dialog for selecting a directory.
        """
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_directory)

    def _scan_and_display_tree(self):
        """
        Scans the directory and displays its structure in a tree view.
        """
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        self.progress_bar.start()
        self.tree.delete(*self.tree.get_children())  # Clear the tree view

        def perform_scan():
            try:
                self._build_tree(directory)
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.progress_bar.stop()

        threading.Thread(target=perform_scan).start()

    def _build_tree(self, root_dir):
        """
        Builds and displays the directory tree.

        Args:
            root_dir (str): The root directory to scan.
        """
        def populate_treeview(tree, parent, path):
            try:
                for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                    item_path = os.path.join(path, item)
                    is_dir = os.path.isdir(item_path)
                    size = calculate_size(item_path)
                    size_text = format_file_size(size)
                    # Add current item to the tree
                    node_id = tree.insert(parent, "end", text=item, values=(size_text,), open=False)
                    if is_dir:
                        # Recursively populate tree for subdirectories
                        populate_treeview(tree, node_id, item_path)
            except PermissionError:
                pass  # Ignore directories that cannot be accessed

        # Add the root directory to the tree view
        root_node = self.tree.insert("", "end", text=os.path.basename(root_dir), values=("Calculating...",), open=True)
        populate_treeview(self.tree, root_node, root_dir)

    def _visualize_disk_usage(self):
        """
        Generates a pie chart to visualize disk usage for the selected directory.
        """
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        def perform_visualization():
            try:
                labels, sizes = visualize_disk_usage(directory)
                plot_disk_usage(labels, sizes)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=perform_visualization).start()

    def _show_top_5_heavy_items(self):
        """
        Displays a message box with the top 5 heaviest files or directories.
        """
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        def fetch_top_5():
            try:
                top_items = get_top_5_heavy_items(directory)
                result = "\n".join([f"{item['name']}: {item['size']}" for item in top_items])
                messagebox.showinfo("Top 5 Largest Items", result)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=fetch_top_5).start()


if __name__ == "__main__":
    app = DiskScannerGUI()
    app.mainloop()
