import os
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from file_size import calculate_size, format_file_size
from tkinter import Toplevel
from tkinter import Label, Canvas, BOTH
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import Toplevel, Label, Frame, BOTH, LEFT
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from tkinter import Toplevel, Frame, Label, BOTH, LEFT
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from tkinter import Toplevel, Frame, Label, BOTH, LEFT
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.colors import to_hex  # Преобразуем цвета в HEX


def plot_disk_usage(labels, sizes, formatted_sizes):
    # Создаем новое окно для графика
    window = Toplevel()
    window.title("Disk Usage Visualization")
    window.geometry("800x600")

    # Настраиваем matplotlib график
    fig = Figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    wedges, texts, autotexts = ax.pie(
        sizes,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops=dict(width=0.3),  # Уменьшаем ширину секторов
        textprops=dict(color="w")
    )
    ax.axis('equal')  # Делаем круг ровным

    # Создаем окно с графиком
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=LEFT, fill=BOTH, expand=True)

    # Добавляем легенду
    legend_frame = Frame(window)
    legend_frame.pack(side=LEFT, fill=BOTH, padx=10)

    for i, (label, size, wedge) in enumerate(zip(labels, formatted_sizes, wedges)):
        # Преобразуем цвет сектора в HEX
        color = to_hex(wedge.get_facecolor()[:3])  # Берем только RGB, игнорируем альфа-канал
        legend_label = Label(
            legend_frame,
            text=f"{label}: {size}",
            bg=color,
            fg="black",
            anchor="w",
            padx=5
        )
        legend_label.pack(fill=BOTH, pady=2)

    # Информационная подпись
    info_label = Label(
        window,
        text="Диск используется следующим образом:",
        font=("Arial", 10),
        anchor="w"
    )
    info_label.pack(side="top", pady=10)




def visualize_disk_usage(path, filters=None):
    """
    Visualize disk usage for the given path with optional filters.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    def apply_filters(item_path):
        if not filters:
            return True
        return any(item_path.endswith(ext.strip()) for ext in filters)

    labels = []
    sizes = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.islink(item_path) or not apply_filters(item_path):  # Skip symbolic links or non-matching items
            continue
        size = calculate_size(item_path)
        if size > 0:
            labels.append(item)
            sizes.append(size)

    if not sizes:
        raise ValueError("No data found for visualization.")

    formatted_sizes = [format_file_size(s) for s in sizes]
    return labels, sizes, formatted_sizes  # Возвращаем все три объекта


