from pathlib import Path
from typing import Any, Optional

import ujson
import re


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


def get_describe_name(text: str) -> Optional[str]:
    """
    获取文本中<color=#FFD780FF>和</color>之间的文本
        :param text: 描述文本
        :return: 名称
    """
    if text := re.search(r'<color=#FFD780FF>(.+?)</color>', text):
        return text[1]
    return None
