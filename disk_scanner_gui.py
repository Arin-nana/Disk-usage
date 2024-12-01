import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from queue import Queue
from disk_scanner import scan_directory, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage
from file_size import format_file_size, calculate_size
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DiskScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Disk Scanner with Filters")
        logging.info("Application started.")
        self.filters_enabled = tk.BooleanVar(value=False)
        self.filters = tk.StringVar()
        self._create_widgets()

    def _create_widgets(self):
        logging.debug("Creating GUI widgets.")
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

        # Loading animation bar
        self.loading_bar = ttk.Progressbar(self, orient="horizontal", mode="indeterminate", length=300)
        self.loading_bar.pack(pady=5)

        # Remaining time label
        self.time_label = tk.Label(self, text="")
        self.time_label.pack(pady=5)

        # Filters section
        tk.Label(self, text="File Type Filters (comma-separated, e.g., .txt,.py):").pack(pady=5)
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=5)
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filters, width=40)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(filter_frame, text="Enable Filters", variable=self.filters_enabled).pack(side=tk.LEFT)

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
            logging.info(f"Directory selected: {selected_directory}")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_directory)
        else:
            logging.warning("No directory selected.")

    def _apply_filters(self, item_path):
        if not self.filters_enabled.get():
            return True
        selected_filters = self.filters.get()
        if not selected_filters:
            return True
        match = any(item_path.endswith(ext.strip()) for ext in selected_filters.split(","))
        logging.debug(f"Filter applied on {item_path}: {'Matched' if match else 'Not matched'}")
        return match

    def _scan_and_display_tree(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            logging.error(f"Invalid directory: {directory}")
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return
        logging.info(f"Scanning directory: {directory}")
        self.tree.delete(*self.tree.get_children())
        self.progress_bar['value'] = 0
        self.time_label['text'] = ""
        self.loading_bar.start()
        self._scan_directory_with_progress(directory)

    def _scan_directory_with_progress(self, directory):
        logging.info("Scanning directory with progress tracking.")
        progress_queue = Queue()
        start_time = time.time()
        visited_paths = set()

        def populate_treeview(tree, parent, path):
            """
            Populate the TreeView widget with directory items.
            """
            try:
                for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                    item_path = os.path.join(path, item)

                    # Проверяем символические ссылки
                    if os.path.islink(item_path):
                        resolved_path = os.path.realpath(item_path)
                        if resolved_path in visited_paths:
                            logging.debug(f"Skipping cyclic symlink: {item_path} -> {resolved_path}")
                            continue
                        # Добавляем разрешённый путь и исходный путь символической ссылки
                        visited_paths.add(resolved_path)
                        visited_paths.add(item_path)

                    else:
                        if item_path in visited_paths:
                            logging.debug(f"Skipping already visited path: {item_path}")
                            continue
                        visited_paths.add(item_path)

                    is_dir = os.path.isdir(item_path)
                    if not is_dir and not self._apply_filters(item_path):
                        continue

                    size = calculate_size(item_path)
                    size_text = format_file_size(size)
                    node_id = tree.insert(parent, "end", text=item, values=(size_text,), open=False)

                    # Если это директория, выполняем рекурсивный вызов
                    if is_dir:
                        populate_treeview(tree, node_id, item_path)
                    progress_queue.put(1)
            except PermissionError:
                logging.warning(f"Permission denied: {path}")
            except FileNotFoundError:
                logging.warning(f"Path not found: {path}")

        def update_progress_bar():
            completed_items = 0
            while completed_items < len(visited_paths):
                completed_items += progress_queue.get()
                elapsed_time = time.time() - start_time
                remaining_time = max(0, elapsed_time * (len(visited_paths) - completed_items) / max(1, completed_items))
                self.time_label["text"] = f"Estimated remaining time: {remaining_time:.2f} seconds"
                self.progress_bar["value"] = (completed_items / len(visited_paths)) * 100
                self.update_idletasks()

            self.loading_bar.stop()
            self.time_label["text"] = "Scan complete!"
            logging.info("Directory scan complete.")

        root_node = self.tree.insert("", "end", text=os.path.basename(directory), values=("Calculating...",), open=True)
        threading.Thread(target=populate_treeview, args=(self.tree, root_node, directory)).start()
        threading.Thread(target=update_progress_bar).start()

    def _visualize_disk_usage(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            logging.error(f"Invalid directory: {directory}")
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return
        logging.info(f"Visualizing disk usage for: {directory}")

        def perform_visualization():
            self.loading_bar.start()
            try:
                filters = self.filters.get().split(",") if self.filters_enabled.get() else None
                labels, sizes, formatted_sizes = visualize_disk_usage(directory, filters)
                plot_disk_usage(labels, sizes, formatted_sizes)
            except Exception as e:
                logging.exception("Visualization failed.")
                messagebox.showerror("Error", str(e))
            finally:
                self.loading_bar.stop()

        threading.Thread(target=perform_visualization).start()

    def _show_top_5_heavy_items(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            logging.error(f"Invalid directory: {directory}")
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return
        logging.info(f"Fetching top 5 largest items from: {directory}")

        def fetch_top_5():
            self.loading_bar.start()
            try:
                filters = self.filters.get().split(",") if self.filters_enabled.get() else None
                top_items = get_top_5_heavy_items(directory, filters)
                result = "\n".join([f"{item['name']}: {item['size']}" for item in top_items])
                messagebox.showinfo("Top 5 Largest Items", result)
                logging.info(f"Top 5 items displayed: {result}")
            except Exception as e:
                logging.exception("Failed to fetch top 5 items.")
                messagebox.showerror("Error", str(e))
            finally:
                self.loading_bar.stop()

        threading.Thread(target=fetch_top_5).start()

if __name__ == "__main__":
    app = DiskScannerGUI()
    app.mainloop()
