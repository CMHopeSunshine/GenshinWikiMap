import time
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import httpx
from PIL import Image

from .api import ASSETS_API


def download_from_ambr(path: Path, is_monster: bool = False):
    """
    从安柏计划下载UI资源。
        :param path: 保存的路径
        :param is_monster: 是否为原魔
        :return: Image对象
    """
    if path.exists():
        return Image.open(path)
    if 'RelicIcon' in path.name:
        name = f'reliquary/{path.name}'
    elif 'MonsterIcon' in path.name:
        name = f'monster/{path.name}'
    else:
        name = path.name
    print(f'下载{ASSETS_API.format(name)}')
    resp = httpx.get(ASSETS_API.format(name), headers={
        'accept':                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':           'gzip, deflate, br',
        'accept-language':           'zh-CN,zh;q=0.9',
        'cache-control':             'max-age=0',
        'referer':                   'https://ambr.top/',
        'User-Agent':                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cookie':                    '_ga=GA1.1.177458924.1663681198; _ym_uid=1663681206452363412; _ym_d=1663681206; __gads=ID=bc0fa7424a8f09d8:T=1663681207:S=ALNI_MZ-AfafN8FcoD4fg2vrmUxImYSxZg; _pubcid=c40ced2c-29d6-401b-8d41-b2687de628ef; _ym_isad=2; __gpi=UID=000009d140c725e2:T=1663681207:RT=1669949024:S=ALNI_MaX_oi5M_jkauQJr0MBiNepTXWeyg; cto_bundle=TWfmwl9jaDZnOVRBS2d5MXFEVkNNdTBPT0w1cXVYVW5DTVhxaWR2Y0FZbERnNUtyZmNJVzBJWFY4JTJGc0IlMkJMbnJvQXBZZVVaJTJCT1pPYm5wRDZUN2hQOUgxUk5VZCUyRkdOSjFsQXlYQkNZd1NlayUyQkxDQmk5NVVuNXNWdllqSnl1VWl3VUcxcUFvJTJCRkV5ZFY3UmdpRW9uUXF1eHplVkElM0QlM0Q; cto_bidid=1_h_vV9KSTRLNEY0SEtjRWUlMkZ0SE1Cd25oREZ2OUg3cUtnQmdNUmZNcHNYJTJGT0xmU0xUJTJCdHZmWlYwcDlFJTJGYXUySzklMkYxJTJCalo3ZCUyQkhoY0dhNWpkellpTHo0bDAlMkZncDRWUkZPZSUyQjhHaFdsN25tYVM3QSUzRA; _ga_L8G8CTDTKD=GS1.1.1669949013.34.1.1669949039.0.0.0',
        'sec-ch-ua':                 '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile':          '?0',
        'sec-ch-ua-platform':        '"Windows"',
        'sec-fetch-dest':            'document',
        'sec-fetch-mode':            'navigate',
        'sec-fetch-site':            'none',
        'sec-fetch-user':            '?1',
        'upgrade-insecure-requests': '1'
    }, timeout=10)
    content = resp.content
    img = Image.open(BytesIO(content))
    with path.open('wb') as f:
        f.write(content)
    time.sleep(1)  # 安柏网有访问频率限制
    return img


def ambr_requests(api: str):
    """
    从安柏计划发送请求获取数据。
        :param api: 安柏API
        :return: 数据
    """
    resp = httpx.get(api, headers={
        'referer':    'https://ambr.top/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cookie':     '_ga=GA1.1.177458924.1663681198; _ym_uid=1663681206452363412; _ym_d=1663681206; __gads=ID=bc0fa7424a8f09d8:T=1663681207:S=ALNI_MZ-AfafN8FcoD4fg2vrmUxImYSxZg; _pubcid=c40ced2c-29d6-401b-8d41-b2687de628ef; _ym_isad=2; __gpi=UID=000009d140c725e2:T=1663681207:RT=1669949024:S=ALNI_MaX_oi5M_jkauQJr0MBiNepTXWeyg; cto_bundle=TWfmwl9jaDZnOVRBS2d5MXFEVkNNdTBPT0w1cXVYVW5DTVhxaWR2Y0FZbERnNUtyZmNJVzBJWFY4JTJGc0IlMkJMbnJvQXBZZVVaJTJCT1pPYm5wRDZUN2hQOUgxUk5VZCUyRkdOSjFsQXlYQkNZd1NlayUyQkxDQmk5NVVuNXNWdllqSnl1VWl3VUcxcUFvJTJCRkV5ZFY3UmdpRW9uUXF1eHplVkElM0QlM0Q; cto_bidid=1_h_vV9KSTRLNEY0SEtjRWUlMkZ0SE1Cd25oREZ2OUg3cUtnQmdNUmZNcHNYJTJGT0xmU0xUJTJCdHZmWlYwcDlFJTJGYXUySzklMkYxJTJCalo3ZCUyQkhoY0dhNWpkellpTHo0bDAlMkZncDRWUkZPZSUyQjhHaFdsN25tYVM3QSUzRA; _ga_L8G8CTDTKD=GS1.1.1669949013.34.1.1669949039.0.0.0',
    })
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def github_requests(url: str):
    """
    向github发送请求获取数据。
        :param url: github url
        :return: 数据
    """
    try:
        resp = httpx.get(url, timeout=10)
    except Exception:
        resp = httpx.get(f'https://ghproxy.com/{url}', timeout=10)
    return resp.json() if resp.status_code == 200 else None
