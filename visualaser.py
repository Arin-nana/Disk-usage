import matplotlib.pyplot as plt

from GetSize import convert_size

def visualize_memory_usage(data, total_size):
    data = filer_data(data, total_size)
    sizes = []

    for name, size in data:
        sizes.append(size)

    cmap = plt.get_cmap('tab20')
    colors = [cmap(i % cmap.N) for i in range(len(data))]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=None, autopct=lambda p: f"{p:.2f}%" if p > 2 else "", colors=colors)
    ax.set_title(f"Общий размер {convert_size(total_size)}")

    if len(sizes) % 35 == 0:
        legend_cols = len(sizes) // 35
    else:
        legend_cols = len(sizes) // 35 + 1

    legend_handles = [f"{name} - {convert_size(size)}" for name, size in data]
    legend_handles = [legend_handles[i:i + legend_cols] for i in range(0, len(legend_handles), legend_cols)]

    all_handles = [item for sublist in legend_handles for item in sublist]
    plt.legend(all_handles, loc="upper left", bbox_to_anchor=(0.9, 1), ncol=legend_cols)

    plt.subplots_adjust(left=-0.5)

    plt.show()

def filer_data(data, total_size):
    result = [(name, size) for name, size in data if size / total_size > 0.02]
    othersize = sum(size for name, size in data if size / total_size <= 0.02)
    if othersize > 0:
        result.append(("other", othersize))
    return result