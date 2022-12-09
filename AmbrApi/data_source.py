import time
from io import BytesIO
from pathlib import Path
from typing import Optional

import httpx
from PIL import Image

from .api import *

HEADERS = {
    'referer':    'https://ambr.top/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Cookie':     '_ga=GA1.1.177458924.1663681198; _ym_uid=1663681206452363412; _ym_d=1663681206; __gads=ID=bc0fa7424a8f09d8:T=1663681207:S=ALNI_MZ-AfafN8FcoD4fg2vrmUxImYSxZg; _pubcid=c40ced2c-29d6-401b-8d41-b2687de628ef; _ym_isad=2; __gpi=UID=000009d140c725e2:T=1663681207:RT=1669949024:S=ALNI_MaX_oi5M_jkauQJr0MBiNepTXWeyg; cto_bundle=TWfmwl9jaDZnOVRBS2d5MXFEVkNNdTBPT0w1cXVYVW5DTVhxaWR2Y0FZbERnNUtyZmNJVzBJWFY4JTJGc0IlMkJMbnJvQXBZZVVaJTJCT1pPYm5wRDZUN2hQOUgxUk5VZCUyRkdOSjFsQXlYQkNZd1NlayUyQkxDQmk5NVVuNXNWdllqSnl1VWl3VUcxcUFvJTJCRkV5ZFY3UmdpRW9uUXF1eHplVkElM0QlM0Q; cto_bidid=1_h_vV9KSTRLNEY0SEtjRWUlMkZ0SE1Cd25oREZ2OUg3cUtnQmdNUmZNcHNYJTJGT0xmU0xUJTJCdHZmWlYwcDlFJTJGYXUySzklMkYxJTJCalo3ZCUyQkhoY0dhNWpkellpTHo0bDAlMkZncDRWUkZPZSUyQjhHaFdsN25tYVM3QSUzRA; _ga_L8G8CTDTKD=GS1.1.1669949013.34.1.1669949039.0.0.0',
}


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
    print(f'下载{path.name}')
    resp = httpx.get(ASSETS_API.format(path.name), headers={
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


def get_avatar_list() -> Optional[dict[str, dict]]:
    resp = httpx.get(AVATAR_LIST_API, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']['items']
    return None


def get_avatar_info(avatar_id: str) -> Optional[dict]:
    resp = httpx.get(AVATAR_INFO_API.format(avatar_id), headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def get_material_list() -> Optional[dict[str, dict]]:
    resp = httpx.get(MATERIAL_LIST_API, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def get_material_info(material_id: str) -> Optional[dict]:
    resp = httpx.get(MATERIAL_INFO_API.format(material_id), headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def get_avatar_curve() -> Optional[dict]:
    resp = httpx.get(AVATAR_CURVE_API, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def get_weapon_curve() -> Optional[dict]:
    resp = httpx.get(WEAPON_CURVE_API, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def get_prop_map() -> Optional[dict]:
    resp = httpx.get(PROP_MAP_API, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None


def get_artifact_list() -> Optional[dict]:
    resp = httpx.get(ARTIFACT_LIST_API, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']['items']
    return None


def get_artifact_info(artifact_id: str) -> Optional[dict]:
    resp = httpx.get(ARTIFACT_INFO_API.format(artifact_id), headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data['data']
    return None
