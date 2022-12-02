import time
from pathlib import Path
from typing import Any

import ujson
import httpx
from PIL import Image
from io import BytesIO


def load_json(path: Path, encoding: str = 'utf-8'):
    """
    说明：
        读取本地json文件，返回文件数据。
    参数：
        :param path: 文件路径
        :param encoding: 编码，默认为utf-8
        :return: 数据
    """
    if isinstance(path, str):
        path = Path(path)
    return ujson.load(path.open('r', encoding=encoding)) if path.exists() else {}


def save_json(data: Any, path: Path, encoding: str = 'utf-8'):
    """
    说明：
        保存数据到json文件中
    参数：
        :param data: 要保存的数据
        :param path: 保存路径
        :param encoding: 编码，默认为utf-8
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    ujson.dump(data, path.open('w', encoding=encoding), ensure_ascii=False, indent=2)


def download_from_ambr(path: Path):
    """
    说明：
        从安柏计划下载UI资源。
    参数：
        :param path: 保存的路径
        :return: Image对象
    """
    if path.exists():
        return Image.open(path)
    resp = httpx.get(f'https://api.ambr.top/assets/UI/{path.name}', headers={
        'referer': 'https://ambr.top/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    })
    content = resp.content
    img = Image.open(BytesIO(content))
    with path.open('wb') as f:
        f.write(content)
    time.sleep(1)  # 安柏网有访问频率限制
    return img
