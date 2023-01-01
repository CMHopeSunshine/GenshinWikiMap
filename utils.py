from pathlib import Path
from typing import Any

import ujson


def load_json(path: Path, encoding: str = 'utf-8'):
    """
    读取本地json文件，返回文件数据。
        :param path: 文件路径
        :param encoding: 编码，默认为utf-8
        :return: 数据
    """
    return ujson.load(path.open('r', encoding=encoding)) if path.exists() else {}


def save_json(data: Any, path: Path, encoding: str = 'utf-8'):
    """
    保存数据到json文件中
        :param data: 要保存的数据
        :param path: 保存路径
        :param encoding: 编码，默认为utf-8
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    ujson.dump(data, path.open('w', encoding=encoding), ensure_ascii=False, indent=2)
