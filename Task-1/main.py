import os
import zipfile
import json
import datetime
import sys
import argparse


class ShellEmulator:
    def __init__(self, username, computername, zip_path, log_path, script_path):
        self.username = username
        self.computername = computername
        self.log_path = log_path
        self.current_directory = "/home"  # Начнем с домашней директории
        self.virtual_fs_root = "virtual_fs"

        # Загружаем виртуальную файловую систему
        self.load_virtual_fs(zip_path)

        # Создаем или очищаем лог-файл
        open(self.log_path, 'w').close()

        # Выполняем команды из стартового скрипта, если указан
        if script_path:
            self.run_startup_script(script_path)

    def load_virtual_fs(self, zip_path):
        """Загружает виртуальную файловую систему из zip-архива."""
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Файл {zip_path} не найден.")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.virtual_fs_root)

    def log_action(self, action):
        """Логирует действия в JSON-файл."""
        log_entry = {
            "user": self.username,
            "action": action,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(self.log_path, 'a') as log_file:
            json.dump(log_entry, log_file)
            log_file.write('\n')

    def run_startup_script(self, script_path):
        """Выполняет команды из стартового скрипта."""
        if not os.path.exists(script_path):
            print(f"Стартовый скрипт {script_path} не найден.")
            return
        with open(script_path, 'r') as script_file:
            for line in script_file:
                command = line.strip()
                if command:
                    print(f"$ {command}")
                    self.execute_command(command)

    def execute_command(self, command):
        """Обрабатывает и выполняет команды."""
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0]

        if cmd == "ls":
            self.ls()
        elif cmd == "cd":
            if len(parts) > 1:
                self.cd(parts[1])
            else:
                print("cd: ожидается аргумент")
        elif cmd == "who":
            self.who()
        elif cmd == "whoami":
            self.whoami()
        elif cmd == "exit":
            print("Exiting shell.")
            sys.exit(0)
        else:
            print(f"Команда не найдена: {cmd}")

        # Логируем каждую команду
        self.log_action(command)

    def ls(self):
        """Выводит содержимое текущей директории."""
        abs_path = os.path.join(self.virtual_fs_root, self.current_directory.lstrip("/"))

        if not os.path.exists(abs_path):
            print("Directory not found")
            return

        items = os.listdir(abs_path)
        directories = [d for d in items if os.path.isdir(os.path.join(abs_path, d))]
        files = [f for f in items if os.path.isfile(os.path.join(abs_path, f))]

        print("Directories:", " ".join(directories) if directories else "None")
        print("Files:", " ".join(files) if files else "None")

    def cd(self, path):
        """Изменяет текущую директорию."""
        # Если указано "/", переходим в корень виртуальной файловой системы
        if path == "/":
            self.current_directory = "/"
            return

        # Формируем новый путь, нормализуем и удаляем начальный слеш
        new_path = os.path.normpath(os.path.join(self.current_directory, path))

        # Полный путь относительно корня виртуальной файловой системы
        abs_new_path = os.path.join(self.virtual_fs_root, new_path.lstrip("/"))

        # Проверяем, что директория существует и является директорией
        if os.path.isdir(abs_new_path):
            self.current_directory = new_path
        else:
            print(f"No such directory: {path}")

    def who(self):
        """Выводит имя текущего пользователя."""
        print(self.username)

    def whoami(self):
        """Выводит имя текущего пользователя (аналог who)."""
        print(self.username)

    def start(self):
        """Запускает основной цикл командной строки эмулятора."""
        while True:
            command = input(f"{self.username}@{self.computername}:{self.current_directory}$ ")
            self.execute_command(command)


def main():
    parser = argparse.ArgumentParser(description="Эмулятор Shell")
    parser.add_argument("--user", required=True, help="Имя пользователя для приглашения")
    parser.add_argument("--computer", required=True, help="Имя компьютера для приглашения")
    parser.add_argument("--zip_path", required=True, help="Путь к zip-архиву виртуальной файловой системы")
    parser.add_argument("--log_path", required=True, help="Путь к лог-файлу")
    parser.add_argument("--script_path", help="Путь к стартовому скрипту")
    args = parser.parse_args()

    shell = ShellEmulator(args.user, args.computer, args.zip_path, args.log_path, args.script_path)
    shell.start()


if __name__ == "__main__":
    main()
