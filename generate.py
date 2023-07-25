import zipfile
import hashlib
from pathlib import Path

from utils import save_json

DATA = Path() / 'data'
single_file = ['元素精通系数', '原魔列表', '圣遗物信息', '圣遗物列表', '有效词条', '武器列表', '武器类型', '类型', '角色列表', '属性Map']

json_data = {
    'avatar':   [],
    'weapon':   [],
    'artifact': []
}

for type, value in json_data.items():
    for file in (DATA / type).iterdir():
        if file.suffix == '.json':
            value.append(
                {
                    'name': file.stem,
                    'hash': hashlib.md5(file.read_bytes()).hexdigest(),
                }
            )

json_data['data'] = [{
    'name': (path := DATA / f'{file}.json').stem,
    'hash': hashlib.md5(path.read_bytes()).hexdigest()
} for file in single_file]

save_json(json_data, DATA / 'data_list.json')

with zipfile.ZipFile(DATA / 'data.zip', 'w', zipfile.ZIP_STORED) as f:
    for file in DATA.rglob('*'):
        if file.suffix == '.zip':
            continue
        if file.name == 'raw' or file.parent.name == 'raw' or file.parent.parent.name == 'raw':
            continue
        if file.is_file() and file.stem not in single_file and file.parent.name == 'data':
            continue
        f.write(file, str(file).replace('\\', '/').lstrip('data').lstrip('/'))


with zipfile.ZipFile(Path() / 'resources' / 'genshin_resources.zip', 'w', zipfile.ZIP_DEFLATED) as f:
    for dir_type in ['talent', 'material', 'avatar', 'avatar_side', 'weapon', 'artifact']:
        for file in (Path() / 'resources' / dir_type).iterdir():
            f.write(file, str(file).replace('\\', '/').lstrip('resources').lstrip('/'))

with zipfile.ZipFile(Path() / 'resources' / 'genshin_splash.zip', 'w', zipfile.ZIP_DEFLATED) as f:
    for file in (Path() / 'resources' / "splash").iterdir():
        f.write(file, file.name)