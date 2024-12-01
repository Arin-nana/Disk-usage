import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from queue import Queue
from disk_scanner import scan_directory, get_top_5_heavy_items
from visualizer import visualize_disk_usage, plot_disk_usage
from file_size import format_file_size, calculate_size
import time




class DiskScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Disk Scanner with Filters")
        self.filters_enabled = tk.BooleanVar(value=False)  # Переменная для переключения фильтров
        self.filters = tk.StringVar()  # Хранение выбранных фильтров
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

    def _scan_directory_with_progress(self, directory):
        """
        Выполняет сканирование каталога с учетом фильтров и обновляет прогресс-бар.
        """
        progress_queue = Queue()
        start_time = time.time()

        # Подсчет общего числа элементов с учетом фильтров
        def count_filtered_items(path):
            total = 0
            for root, dirs, files in os.walk(path):
                # Учитываем только директории и файлы, прошедшие фильтр
                total += len([d for d in dirs if self._apply_filters(os.path.join(root, d))])
                total += len([f for f in files if self._apply_filters(os.path.join(root, f))])
            return total

        total_items = count_filtered_items(directory)

        def populate_treeview(tree, parent, path):
            """
            Рекурсивно добавляет элементы в TreeView и обновляет очередь прогресса.
            """
            try:
                for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                    item_path = os.path.join(path, item)
                    is_dir = os.path.isdir(item_path)

                    # Применение фильтрации
                    if not is_dir and not self._apply_filters(item_path):
                        continue

                    size = calculate_size(item_path)
                    size_text = format_file_size(size)
                    node_id = tree.insert(parent, "end", text=item, values=(size_text,), open=False)
                    if is_dir:
                        populate_treeview(tree, node_id, item_path)
                    progress_queue.put(1)
            except PermissionError:
                pass

        def update_progress_bar():
            completed_items = 0
            smooth_elapsed_times = []
            while completed_items < total_items:
                completed_items += progress_queue.get()
                elapsed_time = time.time() - start_time
                smooth_elapsed_times.append(elapsed_time / completed_items * total_items)
                smooth_elapsed_times = smooth_elapsed_times[-10:]  # Оставляем последние 10 замеров

                remaining_time = max(0, sum(smooth_elapsed_times) / len(smooth_elapsed_times) - elapsed_time)
                self.time_label['text'] = f"Estimated remaining time: {remaining_time:.2f} seconds"

                self.progress_bar['value'] = (completed_items / total_items) * 100
                self.update_idletasks()
            self.loading_bar.stop()
            self.time_label['text'] = "Scan complete!"

        root_node = self.tree.insert("", "end", text=os.path.basename(directory), values=("Calculating...",), open=True)
        threading.Thread(target=populate_treeview, args=(self.tree, root_node, directory)).start()
        threading.Thread(target=update_progress_bar).start()

    def _browse_directory(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_directory)

    def _apply_filters(self, item_path):
        """
        Применяет фильтры к файлам.
        Возвращает True, если файл соответствует фильтру, и False в противном случае.
        """
        if not self.filters_enabled.get():  # Если фильтры отключены
            return True
        selected_filters = self.filters.get()
        if not selected_filters:
            return True  # Без указанных фильтров обрабатываем все файлы
        return any(item_path.endswith(ext.strip()) for ext in selected_filters.split(","))

    def _scan_and_display_tree(self):
        """
        Основной метод для сканирования каталога и отображения дерева.
        """
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        self.tree.delete(*self.tree.get_children())  # Очищаем дерево
        self.progress_bar['value'] = 0
        self.time_label['text'] = ""
        self.loading_bar.start()  # Запускаем анимацию загрузки

        self._scan_directory_with_progress(directory)

    def _visualize_disk_usage(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        def perform_visualization():
            self.loading_bar.start()  # Запускаем анимацию загрузки
            try:
                filters = self.filters.get().split(",") if self.filters_enabled.get() else None
                labels, sizes, formatted_sizes = visualize_disk_usage(directory, filters)
                plot_disk_usage(labels, sizes, formatted_sizes)
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.loading_bar.stop()  # Останавливаем анимацию загрузки

        threading.Thread(target=perform_visualization).start()
    def _show_top_5_heavy_items(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
            return

        def fetch_top_5():
            self.loading_bar.start()  # Запускаем анимацию загрузки
            try:
                filters = self.filters.get().split(",") if self.filters_enabled.get() else None
                top_items = get_top_5_heavy_items(directory, filters)
                result = "\n".join([f"{item['name']}: {item['size']}" for item in top_items])
                messagebox.showinfo("Top 5 Largest Items", result)
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.loading_bar.stop()  # Останавливаем анимацию загрузки

        threading.Thread(target=fetch_top_5).start()

if __name__ == "__main__":
    app = DiskScannerGUI()
    app.mainloop()