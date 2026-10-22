"""Операции над путями VFS: разбор и нормализация."""

PATH_SEPARATOR = "/"
ROOT_PATH = PATH_SEPARATOR
CURRENT_DIR = "."
PARENT_DIR = ".."


def split_path(path):
    """Разбивает путь на имена, отбрасывая пустые части и '.'."""
    return [part for part in path.split(PATH_SEPARATOR)
            if part and part != CURRENT_DIR]


def join_parts(parts):
    """Собирает абсолютный путь из списка имён."""
    return PATH_SEPARATOR + PATH_SEPARATOR.join(parts)


def normalize_path(cwd, path):
    """Возвращает абсолютный путь без '.', '..' и повторных '/'.

    Относительный путь отсчитывается от каталога cwd; '..' в корне
    остаётся в корне, как в UNIX.
    """
    parts = [] if path.startswith(PATH_SEPARATOR) else split_path(cwd)
    for part in split_path(path):
        if part == PARENT_DIR:
            parts = parts[:-1]
        else:
            parts.append(part)
    return join_parts(parts)
