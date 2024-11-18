<<<<<<< Updated upstream
# Disk Scanner

**Disk Scanner** — это инструмент на Python для анализа использования диска. Он предоставляет как интерфейс командной строки (CLI), так и графический интерфейс (GUI) для сканирования директорий, визуализации использования диска и выявления самых крупных файлов и папок на вашей системе.
=======
# Disk Usage

**Disk Usage** — это инструмент на Python для анализа использования диска. Он предоставляет как интерфейс командной строки (CLI), так и графический интерфейс (GUI) для сканирования директорий, визуализации использования диска и выявления самых крупных файлов и папок на вашей системе.
>>>>>>> Stashed changes

## Особенности

- **Сканирование директорий**: Рекурсивное сканирование директорий с отображением их структуры в виде дерева.
- **Визуализация использования диска**: Построение графиков (например, круговых диаграмм) для наглядного отображения использования диска.
- **Топ-5 самых крупных объектов**: Определение и отображение 5 самых больших файлов или папок в указанном пути.
- **Графический интерфейс**: Удобный GUI на основе Tkinter для легкого взаимодействия.
- **Интерфейс командной строки**: Возможность работы через терминал.
<<<<<<< Updated upstream

## Использование

### Интерфейс командной строки

Запустите интерфейс командной строки с помощью команды:

```bash
python interface.py
```

#### Пример

```
=== Disk Scanner ===
1. Сканировать директорию и отобразить структуру
2. Визуализировать использование диска
3. Показать топ-5 самых крупных объектов
4. Выход
Введите ваш выбор: 1
Введите путь к директории для сканирования: /path/to/directory

Структура директории:
> directory
    [DIR] subdirectory
        file1.txt - 1.0 MB
        file2.txt - 2.0 MB
    file3.txt - 500 KB
```

### Графический интерфейс (GUI)

Запустите графический интерфейс с помощью команды:

```bash
python disk_scanner_gui.py
```

- **Сканирование и отображение структуры**: Сканирует выбранную директорию и отображает её структуру в виде дерева.
- **Визуализация использования диска**: Генерирует круговую диаграмму, показывающую использование диска в выбранной директории.
- **Показать топ-5 самых крупных объектов**: Отображает список из 5 самых больших файлов или директорий в указанном пути.

## Файлы

- `disk_scanner.py`: Основной функционал для сканирования директорий и поиска крупных объектов.
- `disk_scanner_gui.py`: GUI-приложение на базе Tkinter.
- `file_size.py`: Утилиты для расчёта и форматирования размеров файлов.
- `interface.py`: Интерфейс командной строки.
- `visualizer.py`: Функции для визуализации использования диска с помощью matplotlib.

## Требования

Список зависимостей находится в файле `requirements.txt`.

=======

## Установка

### Требования

- Python 3.x
- Менеджер пакетов `pip`


## Использование

### Интерфейс командной строки

Запустите интерфейс командной строки с помощью команды:

```bash
python interface.py
```

#### Пример

```
=== Disk Scanner ===
1. Сканировать директорию и отобразить структуру
2. Визуализировать использование диска
3. Показать топ-5 самых крупных объектов
4. Выход
Введите ваш выбор: 1
Введите путь к директории для сканирования: C:\Users\1\OneDrive\Doc\GitHub\Disk-usage

Структура директории:
> directory
    [DIR] subdirectory
        file1.txt - 1.0 MB
        file2.txt - 2.0 MB
    file3.txt - 500 KB
```

### Графический интерфейс (GUI)

Запустите графический интерфейс с помощью команды:

```bash
python disk_scanner_gui.py
```

- **Сканирование и отображение структуры**: Сканирует выбранную директорию и отображает её структуру в виде дерева.
- **Визуализация использования диска**: Генерирует круговую диаграмму, показывающую использование диска в выбранной директории.
- **Показать топ-5 самых крупных объектов**: Отображает список из 5 самых больших файлов или директорий в указанном пути.

## Файлы

- `disk_scanner.py`: Основной функционал для сканирования директорий и поиска крупных объектов.
- `disk_scanner_gui.py`: GUI-приложение на базе Tkinter.
- `file_size.py`: Утилиты для расчёта и форматирования размеров файлов.
- `interface.py`: Интерфейс командной строки.
- `visualizer.py`: Функции для визуализации использования диска с помощью matplotlib.

## Требования

Список зависимостей находится в файле `requirements.txt`.
>>>>>>> Stashed changes
