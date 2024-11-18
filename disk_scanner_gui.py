import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import matplotlib.pyplot as plt
from file_size import calculate_size

# Функция для сканирования директории
def scan_directory(path, extension_filter=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")
    contents = []
    for root, dirs, files in os.walk(path):
        for item in dirs + files:
            item_path = os.path.join(root, item)
            if extension_filter and not item.endswith(extension_filter):
                continue
            item_type = "Directory" if os.path.isdir(item_path) else "File"
            item_size = calculate_size(item_path)
            contents.append({"type": item_type, "name": item, "size": item_size})
    if not contents:
        raise ValueError(f"No files or directories found in '{path}'.")
    return contents

# Функция для визуализации использования диска
def visualize_disk_usage(path, extension_filter=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")
    data = []
    labels = []
    for root, dirs, files in os.walk(path):
        for item in dirs + files:
            item_path = os.path.join(root, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                if extension_filter and not item.endswith(extension_filter):
                    continue
                size = calculate_size(item_path)
                data.append(size)
                labels.append(item)
    if not data:
        raise ValueError("No data found for visualization.")
    return labels, data

# Функция для создания графика
def plot_disk_usage(labels, sizes):
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    plt.title("Disk Usage Visualization")
    plt.show()

# Функция для обработки кнопки "Scan Directory"
def scan_directory_gui():
    directory = path_entry.get()
    extension = extension_entry.get().strip() or None
    if not os.path.isdir(directory):
        messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
        return
    progress_bar.start()
    results_text.delete(1.0, tk.END)  # Clear previous results
    def perform_scan():
        try:
            contents = scan_directory(directory, extension_filter=extension)
            for item in contents:
                results_text.insert(tk.END, f"{item['type']}: {item['name']} ({item['size']} bytes)\n")
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
        except ValueError as e:
            messagebox.showinfo("Info", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            progress_bar.stop()
    threading.Thread(target=perform_scan).start()

# Функция для обработки кнопки "Visualize Disk Usage"
def visualize_disk_usage_gui():
    directory = path_entry.get()
    extension = extension_entry.get().strip() or None
    if not os.path.isdir(directory):
        messagebox.showerror("Error", f"'{directory}' is not a valid directory.")
        return
    progress_bar.start()
    def perform_visualization():
        try:
            labels, sizes = visualize_disk_usage(directory, extension_filter=extension)
            progress_bar.stop()
            plot_disk_usage(labels, sizes)
        except FileNotFoundError as e:
            progress_bar.stop()
            messagebox.showerror("Error", str(e))
        except ValueError as e:
            progress_bar.stop()
            messagebox.showinfo("Info", str(e))
        except Exception as e:
            progress_bar.stop()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    threading.Thread(target=perform_visualization).start()

# Функция для выбора директории через проводник
def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, selected_directory)

# Создаем основное окно приложения
root = tk.Tk()
root.title("Disk Scanner with Visualization")

# Метки и поля ввода
tk.Label(root, text="Enter directory path:").pack(pady=5)
frame = tk.Frame(root)
frame.pack(pady=5)
path_entry = tk.Entry(frame, width=50)
path_entry.pack(side=tk.LEFT, padx=5)
browse_button = tk.Button(frame, text="Browse", command=browse_directory)
browse_button.pack(side=tk.LEFT)

tk.Label(root, text="Enter file extension (optional):").pack(pady=5)
extension_entry = tk.Entry(root, width=50)
extension_entry.pack(pady=5)
tk.Label(root, text="Example: .txt").pack(pady=5)

# Прогресс-бар
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="indeterminate", length=300)
progress_bar.pack(pady=10)

# Кнопки
tk.Button(root, text="Scan Directory", command=scan_directory_gui).pack(pady=5)
tk.Button(root, text="Visualize Disk Usage", command=visualize_disk_usage_gui).pack(pady=5)

# Поле для вывода результатов сканирования
results_text = tk.Text(root, height=15, width=80, wrap="none")
results_text.pack(pady=5)

# Добавляем возможность выделения и копирования
scrollbar = tk.Scrollbar(root, command=results_text.yview)
results_text.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Запуск главного цикла
root.mainloop()
