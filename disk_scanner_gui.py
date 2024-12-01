import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from queue import Queue
from disk_scanner import calculate_total_items, get_top_5_heavy_items
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
        self.total_items = 0
        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Enter directory path:").pack(pady=5)

        frame = tk.Frame(self)
        frame.pack(pady=5)
        self.path_entry = tk.Entry(frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Browse", command=self._browse_directory).pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=300)
        self.progress_bar.pack(pady=10)

        self.loading_bar = ttk.Progressbar(self, orient="horizontal", mode="indeterminate", length=300)
        self.loading_bar.pack(pady=5)

        self.time_label = tk.Label(self, text="")
        self.time_label.pack(pady=5)

        tk.Label(self, text="File Type Filters (comma-separated, e.g., .txt,.py):").pack(pady=5)
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=5)
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filters, width=40)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(filter_frame, text="Enable Filters", variable=self.filters_enabled).pack(side=tk.LEFT)

        tk.Button(self, text="Scan and Display Tree", command=self._scan_and_display_tree).pack(pady=5)
        tk.Button(self, text="Visualize Disk Usage", command=self._visualize_disk_usage).pack(pady=5)
        tk.Button(self, text="Show Top 5 Largest Items", command=self._show_top_5_heavy_items).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("size"), displaycolumns=("size"))
        self.tree.heading("#0", text="Directory Structure", anchor="w")
        self.tree.heading("size", text="Size", anchor="w")
        self.tree.column("size", anchor="w", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def _apply_filters(self, file_path):
        """Проверяет, соответствует ли файл указанным фильтрам."""
        if not self.filters_enabled.get():  # Если фильтры отключены, возвращаем True
            return True
        filters = [f.strip() for f in self.filters.get().split(",") if f.strip()]
        return any(file_path.lower().endswith(f.lower()) for f in filters) if filters else True

    def _browse_directory(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            logging.info(f"Directory selected: {selected_directory}")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_directory)
        else:
            logging.warning("No directory selected.")

    def _scan_and_display_tree(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return
        self.tree.delete(*self.tree.get_children())
        self.progress_bar['value'] = 0
        self.time_label['text'] = ""
        self.loading_bar.start()
        self.total_items = calculate_total_items(directory)
        self._scan_directory_with_progress(directory)

    def _scan_directory_with_progress(self, directory):
        visited_paths = set()
        progress_queue = Queue()
        start_time = time.time()

        def populate_treeview(tree, parent, path):
            """Populate the TreeView widget."""
            try:
                iteration_count = 0  # Счётчик итераций
                update_interval = 10  # Частота обновления прогресса (каждые 10 итераций)
                for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                    item_path = os.path.join(path, item)

                    # Если это символическая ссылка, игнорируем её
                    if os.path.islink(item_path):
                        logging.info(f"Ignoring symbolic link: {item_path}")
                        continue

                    # Проверяем, если путь уже посещался
                    if item_path in visited_paths:
                        logging.debug(f"Skipping already visited path: {item_path}")
                        continue
                    visited_paths.add(item_path)

                    is_dir = os.path.isdir(item_path)

                    # Пропускаем файлы, которые не проходят фильтр
                    if not is_dir and not self._apply_filters(item_path):
                        logging.info(f"Skipping file {item_path} due to filter.")
                        continue

                    size = calculate_size(item_path)
                    size_text = format_file_size(size)
                    node_id = tree.insert(parent, "end", text=item, values=(size_text,), open=False)

                    # Рекурсивно обрабатываем директории, если они прошли фильтр
                    if is_dir:
                        if self._apply_filters(item_path):  # Только обрабатываем директории, которые прошли фильтр
                            logging.info(f"Check file {item_path} ")
                            populate_treeview(tree, node_id, item_path)
                        else:
                            logging.info(f"Skipping directory {item_path} due to filter.")
                    if iteration_count % update_interval == 0:
                        progress_queue.put(1)  # Сообщение для обновления прогресса
                    iteration_count += 1
                    progress_queue.put(1)
            except Exception as e:
                logging.error(f"Error populating treeview: {e}")

        def update_progress_bar():
            completed_items = 0
            last_n_times = []
            while completed_items < self.total_items:
                completed_items += progress_queue.get()
                processing_time = time.time() - start_time
                if len(last_n_times) >= 10:
                    last_n_times.pop(0)
                last_n_times.append(processing_time)
                avg_time_per_item = sum(last_n_times) / len(last_n_times)
                remaining_time = avg_time_per_item * (self.total_items - completed_items)
                self.time_label["text"] = f"Estimated remaining time: {remaining_time:.2f} seconds"
                self.progress_bar["value"] = (completed_items / self.total_items) * 100
                self.update_idletasks()
            self.loading_bar.stop()
            self.time_label["text"] = "Scan complete!"

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
