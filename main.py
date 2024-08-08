import os

from GetSize import convert_size
from recursiveFunction import walk_through_directory_recursive
from recursiveFunction import explore_directory_with_size

def print_interface(size, count):
    print("Размер всего файла:", convert_size(size))
    print("Количество всех файлов:", count,)
    print_interface2()

def print_interface2():
    print("Если хотите закончить работу приложения, напишите exit"
          "\nЕсли хотите очистить экран от прошлых команд, напишите clear"
          "\nЕсли хотите вернуться к прошлой директории напишите back"
          "\nИли же введите новую директорию в таком формате /Users/username/document")

def main():
    print("Введите директорию, с которой надо начать в таком формате /Users/username/document")
    prevdir = []
    while True:
        startDirection = input()
        prevdir.append(os.path.dirname(startDirection))

        if startDirection == "exit" or startDirection == "stop":
            break
        if startDirection == "clear":
            os.system('clear')
            print("Введите директорию, с которой надо начать в таком формате /Users/username/document")
            continue
        if startDirection == "back" and len(prevdir) != 0:
            startDirection = prevdir[0]

        if not os.path.exists(startDirection) or not os.path.isdir(startDirection):
            print("Ошибка: Директория не найдена или не является директорией.")
            print("Введите директорию, с которой надо начать в таком формате /Users/username/document")
            continue

        detailed = input(f"Хотите ли вы получить детальную информацию о размере каждого файла в {os.path.basename(startDirection)}? (yes/no): ").lower()

        if detailed == 'yes':
            count = input("Число - количество вложенностей которую хотите: ")
            detailed2 = input("Надо учитывать файлы для которых нужны права администратора? (yes/no)").lower()
            file_extension = input("Введите расширение файлов для фильтрации (например, txt): ")
            if file_extension == "": file_extension = None

            if detailed2 == "yes" or detailed2 == "":
                explore_directory_with_size(startDirection, count, file_extension)
                print_interface2()
            else:
                explore_directory_with_size(startDirection, count, file_extension,True)
                print_interface2()

        else:
            size, count = walk_through_directory_recursive(startDirection)
            print("Содержимое:", startDirection)
            print_interface(size, count)

if __name__ == "__main__":
    main()