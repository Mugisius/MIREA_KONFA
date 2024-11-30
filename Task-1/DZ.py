import os
import psutil
from colorama import *
init(autoreset=True)


def clear_screen(): # Очищение строк
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def update_com_str(): # Обновление строки
    global prompt
    current_path = os.getcwd()
    prompt = f"{current_path}>"


def who():
    processes = psutil.get_users()
    for process in processes:
        print(process)
   
   
def whoami():
    try:
        username = os.getlogin()
        return username
    except KeyError:
        return "Guest"
        
        
def main():
    update_com_str()

    while True:
        command = input(prompt) # Ввод команды
        args = command.split() # Разбиение на элементы списка введенного текста

        if len(args) == 0:
            continue

        elif args[0] == 'ls':
            if len(args) > 1:
                way = args[1]
            else:
                way = '.'
            try:
                files = os.listdir(way)
                # Проверка директория ли это если нет, то вывод файла без цвета
                for item in files:
                    if os.path.isdir(os.path.join(way, item)): # Путь к директории и название элемента, полный путь до элемента
                        print(Fore.BLUE + item)
                    else:
                        print(item)

            except FileNotFoundError:
                print(Fore.RED + f"ls: невозможно получить доступ '{args[1]}': Нет такого файла или каталога ")


        elif args[0] == 'cd':
            if len(args) > 2:
                print("Введено слишком много аргументов")
            elif len(args) == 1:
                os.chdir("D:\Programm\Projects\pythonProject\project_management\pythonProject")
                update_com_str()
            elif len(args) == 2:
                os.chdir(args[1])
                update_com_str()

        elif args[0] == 'exit':
            break

        elif args[0] == "clear" or args[0] == "clr":
            clear_screen()

        elif args[0] == 'echo':
            if len(args) > 1:
                for word in args[1:]:
                    print(word, end=" ")
            print()
            
        elif args[0] == 'who':
            who()
            
        elif args[0] == 'whoami':
            whoami()
        
        else:
            print(f"Команда '{command}' не найдена.")

if __name__ == "__main__":
    main()