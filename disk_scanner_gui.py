import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from queue import Queue, Empty
from disk_scanner import calculate_total_items, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage
from file_size import format_file_size, calculate_size
import time
import logging

# Настройка логгирования
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
        logging.debug("Initializing widgets.")
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
        logging.debug("Widgets initialized successfully.")


    def count_filtered_items(self, directory):
        """Подсчитывает количество элементов с учетом фильтров, включая символические ссылки."""
        count = 0
        try:
            for root, dirs, files in os.walk(directory, followlinks=True):  # Добавлен параметр followlinks
                # Применение фильтров для файлов
                filtered_files = [f for f in files if self._apply_filters(os.path.join(root, f))]
                count += len(filtered_files)
                count += len(dirs)  # Все папки учитываются
        except Exception as e:
            logging.exception(f"Error counting filtered items in {directory}: {e}")
        return count

    def _apply_filters(self, file_path):
        if not self.filters_enabled.get():
            return True
        filters = [f.strip() for f in self.filters.get().split(",") if f.strip()]
        result = any(file_path.lower().endswith(f.lower()) for f in filters) if filters else True
        logging.debug(f"Applying filters to {file_path}: {result}")
        return result

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
            logging.error(f"Invalid directory: {directory}")
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return
        logging.info(f"Scanning directory: {directory}")
        self.tree.delete(*self.tree.get_children())
        self.progress_bar['value'] = 0
        self.time_label['text'] = ""
        self.loading_bar.start()
        self.total_items = self.count_filtered_items(directory)
        logging.info(f"Total filtered items to scan: {self.total_items}")
        threading.Thread(target=self._scan_directory_with_progress, args=(directory,)).start()

    def _scan_directory_with_progress(self, directory):
        visited_paths = set()
        progress_queue = Queue()
        start_time = time.time()
        SYMLINK_TIMEOUT = 5  # Тайм-аут в секундах для символических ссылок

        def populate_treeview(tree, parent, path):
            try:
                for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                    item_path = os.path.join(path, item)

                    # Проверка на символические ссылки
                    if os.path.islink(item_path):
                        logging.warning(f"Skipping symbolic link: {item_path}")
                        progress_queue.put(1)  # Прогресс отмечается для символической ссылки
                        continue

                    if item_path in visited_paths:
                        logging.debug(f"Skipping already visited path: {item_path}")
                        continue
                    visited_paths.add(item_path)

                    is_dir = os.path.isdir(item_path)
                    if not is_dir and not self._apply_filters(item_path):
                        logging.info(f"Skipping file {item_path} due to filter.")
                        progress_queue.put(1)  # Прогресс отмечается для отфильтрованного файла
                        continue

                    size = calculate_size(item_path)
                    size_text = format_file_size(size)
                    node_id = tree.insert(parent, "end", text=item, values=(size_text,), open=False)

                    # Рекурсивный вызов для директорий
                    if is_dir:
                        logging.debug(f"Entering directory: {item_path}")
                        populate_treeview(tree, node_id, item_path)

                    progress_queue.put(1)  # Прогресс для файла или папки
            except Exception as e:
                logging.exception(f"Error populating treeview: {e}")

        def update_progress_bar():
            completed_items = 0
            last_progress_time = time.time()

            while completed_items < self.total_items:
                try:
                    # Проверка на тайм-аут
                    if time.time() - last_progress_time > SYMLINK_TIMEOUT:
                        logging.warning("No progress detected for a long time. Assuming scan is complete.")
                        break

                    # Обновление прогресса
                    completed_items += progress_queue.get(timeout=0.5)
                    last_progress_time = time.time()  # Обновляем время последнего прогресса

                    elapsed_time = time.time() - start_time
                    remaining_items = self.total_items - completed_items
                    remaining_time = (elapsed_time / completed_items) * remaining_items if completed_items > 0 else 0

                    # Обновление интерфейса
                    self.progress_bar["value"] = (completed_items / self.total_items) * 100
                    self.time_label["text"] = f"Remaining time: {remaining_time:.2f}s"
                    self.update_idletasks()
                except Empty:
                    continue

            # Завершение прогресс-бара
            self.progress_bar["value"] = 100
            logging.info("Scan complete.")
            self.loading_bar.stop()
            self.time_label["text"] = "Scan complete!"

        # Запуск потоков
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
                logging.info("Visualization complete.")
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
                logging.info(f"Top 5 items: {result}")
                messagebox.showinfo("Top 5 Largest Items", result)
            except Exception as e:
                logging.exception("Failed to fetch top 5 items.")
                messagebox.showerror("Error", str(e))
            finally:
                self.loading_bar.stop()

        threading.Thread(target=fetch_top_5).start()

if __name__ == "__main__":
    app = DiskScannerGUI()
    app.mainloop()
