"""Состояние сеанса эмулятора: VFS, текущий каталог и история."""

from dataclasses import dataclass, field

from .paths import ROOT_PATH, normalize_path
from .vfs import VfsDir, find_node


@dataclass
class Session:
    """Сеанс работы: корень VFS, текущий каталог и история команд.

    Без загруженной VFS корнем служит пустой каталог в памяти.
    """

    vfs: object = None
    root: VfsDir = field(default_factory=VfsDir)
    cwd: str = ROOT_PATH
    oldpwd: str = ROOT_PATH
    history: list = field(default_factory=list)

    def absolute(self, path):
        """Преобразует путь пользователя в абсолютный."""
        return normalize_path(self.cwd, path)

    def find(self, path):
        """Находит узел VFS по пути пользователя или возвращает None."""
        return find_node(self.root, self.absolute(path))


def new_session(vfs=None):
    """Создаёт сеанс; корнем становится корень загруженной VFS."""
    session = Session(vfs=vfs)
    if vfs is not None:
        session.root = vfs.root
    return session
