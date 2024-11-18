import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from queue import Queue
from disk_scanner import scan_directory, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage
from file_size import format_file_size, calculate_size


class DiskScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Disk Scanner with Progress Bar")
        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Enter directory path:").pack(pady=5)

        # Path input and browse button
        frame = tk.Frame(self)
        frame.pack(pady=5)
        self.path_entry = tk.Entry(frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse", command=self._browse_directory).pack(side=tk.LEFT)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=300)
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
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_directory)

    def _scan_and_display_tree(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        self.tree.delete(*self.tree.get_children())  # Clear the tree view
        self.progress_bar['value'] = 0

        def perform_scan():
            total_items = sum(len(files) + len(dirs) for _, dirs, files in os.walk(directory))
            progress_queue = Queue()

            def populate_treeview(tree, parent, path):
                try:
                    for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                        item_path = os.path.join(path, item)
                        is_dir = os.path.isdir(item_path)
                        size = calculate_size(item_path)
                        size_text = format_file_size(size)
                        node_id = tree.insert(parent, "end", text=item, values=(size_text,), open=False)
                        if is_dir:
                            populate_treeview(tree, node_id, item_path)
                        progress_queue.put(1)
                except PermissionError:
                    pass

            root_node = self.tree.insert("", "end", text=os.path.basename(directory), values=("Calculating...",), open=True)
            threading.Thread(target=populate_treeview, args=(self.tree, root_node, directory)).start()

            def update_progress_bar():
                completed_items = 0
                while completed_items < total_items:
                    completed_items += progress_queue.get()
                    self.progress_bar['value'] = (completed_items / total_items) * 100
                    self.update_idletasks()

            update_progress_bar()

        threading.Thread(target=perform_scan).start()

    def _visualize_disk_usage(self):
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
