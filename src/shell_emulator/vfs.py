"""Виртуальная файловая система (VFS): загрузка из JSON в память."""

import base64
import binascii
import json
from collections import namedtuple
from dataclasses import dataclass, field

TYPE_DIR = "dir"
TYPE_FILE = "file"
ENCODING_TEXT = "text"
ENCODING_BASE64 = "base64"
PATH_SEPARATOR = "/"
RESERVED_NAMES = (".", "..")
TREE_BRANCH = "|-- "
TREE_LAST = "`-- "
TREE_PIPE = "|   "
TREE_INDENT = "    "

VfsStats = namedtuple("VfsStats", "dirs files size depth")


class VfsError(Exception):
    """Ошибка загрузки или разбора VFS."""


@dataclass
class VfsFile:
    """Файл VFS: содержимое хранится в памяти в виде байтов."""

    data: bytes


@dataclass
class VfsDir:
    """Каталог VFS: отображение имени в вложенный каталог или файл."""

    children: dict = field(default_factory=dict)


@dataclass
class Vfs:
    """Загруженная VFS: путь к источнику и корневой каталог."""

    source: str
    root: VfsDir


def join_path(parent, name):
    """Склеивает путь родительского каталога и имени узла."""
    return parent.rstrip(PATH_SEPARATOR) + PATH_SEPARATOR + name


def check_name(name, where):
    """Проверяет, что имя узла допустимо для VFS."""
    if not name or PATH_SEPARATOR in name or name in RESERVED_NAMES:
        raise VfsError(f"{where}: недопустимое имя узла {name!r}")


def decode_content(content, encoding, where):
    """Преобразует содержимое файла из JSON в байты."""
    if encoding == ENCODING_TEXT:
        return content.encode("utf-8")
    if encoding == ENCODING_BASE64:
        try:
            return base64.b64decode(content, validate=True)
        except (binascii.Error, ValueError):
            raise VfsError(f"{where}: неверные данные base64") from None
    raise VfsError(f"{where}: неизвестная кодировка {encoding!r}")


def parse_file(node, where):
    """Создаёт файл VFS из JSON-узла с типом file."""
    content = node.get("content", "")
    if not isinstance(content, str):
        raise VfsError(f"{where}: content должен быть строкой")
    encoding = node.get("encoding", ENCODING_TEXT)
    return VfsFile(decode_content(content, encoding, where))


def parse_dir(node, where):
    """Создаёт каталог VFS из JSON-узла с типом dir."""
    children = node.get("children", {})
    if not isinstance(children, dict):
        raise VfsError(f"{where}: children должен быть объектом")
    result = VfsDir()
    for name, child in children.items():
        check_name(name, where)
        result.children[name] = parse_node(child, join_path(where, name))
    return result


def parse_node(node, where):
    """Разбирает JSON-узел в каталог или файл, проверяя формат."""
    if not isinstance(node, dict):
        raise VfsError(f"{where}: узел должен быть JSON-объектом")
    kind = node.get("type")
    if kind == TYPE_DIR:
        return parse_dir(node, where)
    if kind == TYPE_FILE:
        return parse_file(node, where)
    raise VfsError(f"{where}: неизвестный тип узла {kind!r}")


def read_json(path):
    """Читает JSON-документ с диска, преобразуя ошибки в VfsError."""
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise VfsError(f"файл не найден: {path}") from None
    except json.JSONDecodeError as error:
        raise VfsError(f"неверный формат JSON в {path}: {error}") from None
    except (OSError, UnicodeDecodeError) as error:
        raise VfsError(f"не удалось прочитать {path}: {error}") from None


def load_vfs(path):
    """Загружает VFS из JSON-файла целиком в память."""
    root = parse_node(read_json(path), PATH_SEPARATOR)
    if not isinstance(root, VfsDir):
        raise VfsError("корень VFS должен быть каталогом")
    return Vfs(path, root)


def iter_nodes(directory, depth=1):
    """Обходит дерево, выдавая пары (узел, глубина вложенности)."""
    for _name, child in sorted(directory.children.items()):
        yield child, depth
        if isinstance(child, VfsDir):
            yield from iter_nodes(child, depth + 1)


def collect_stats(root):
    """Считает каталоги, файлы, суммарный размер и глубину дерева."""
    dirs = files = size = depth = 0
    for node, level in iter_nodes(root):
        depth = max(depth, level)
        if isinstance(node, VfsDir):
            dirs += 1
        else:
            files += 1
            size += len(node.data)
    return VfsStats(dirs, files, size, depth)


def format_summary(vfs):
    """Возвращает краткую сводку о загруженной VFS."""
    stats = collect_stats(vfs.root)
    return f"каталогов: {stats.dirs}, файлов: {stats.files}"


def tree_lines(directory, prefix):
    """Генерирует строки дерева каталога с отступом prefix."""
    items = sorted(directory.children.items())
    for index, (name, child) in enumerate(items):
        last = index == len(items) - 1
        is_dir = isinstance(child, VfsDir)
        branch = TREE_LAST if last else TREE_BRANCH
        yield f"{prefix}{branch}{name}{PATH_SEPARATOR if is_dir else ''}"
        if is_dir:
            extension = TREE_INDENT if last else TREE_PIPE
            yield from tree_lines(child, prefix + extension)


def render_tree(root):
    """Рисует дерево VFS в виде текста."""
    return "\n".join([PATH_SEPARATOR, *tree_lines(root, "")])
