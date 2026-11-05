import getpass
import shlex
import socket


def make_prompt():
    """Приглашение вида username@hostname:~$ из реальных данных ОС."""
    username = getpass.getuser()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$ "


def cmd_ls(args):
    """Заглушка ls: печатает своё имя и аргументы."""
    print(f"ls {args}")


def cmd_cd(args):
    """Заглушка cd: печатает своё имя и аргументы."""
    print(f"cd {args}")


commands = {
    "ls": cmd_ls,
    "cd": cmd_cd,
}


def main():
    """Цикл REPL: ввод -> разбор -> выполнение, пока не exit."""
    prompt = make_prompt()
    while True:
        try:
            line = input(prompt)
        except EOFError:
            print()
            break

        try:
            parts = shlex.split(line)
        except ValueError:
            print("ошибка: неверные аргументы (не закрыта кавычка)")
            continue

        if not parts:
            continue

        name = parts[0]
        args = parts[1:]

        if name == "exit":
            if args:
                print("exit: ошибка: неверные аргументы")
                continue
            break
        if name in commands:
            commands[name](args)
        else:
            print(f"{name}: команда не найдена")


if __name__ == "__main__":
    main()