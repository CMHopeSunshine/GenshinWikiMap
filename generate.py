import zipfile
import hashlib

from path import DATA
from utils import save_json

single_file = ['元素精通系数', '原魔列表', '圣遗物信息', '圣遗物列表', '有效词条', '武器列表', '武器类型', '类型', '角色列表', '属性Map']

json_data = {
    'avatar':   [],
    'weapon':   [],
    'artifact': []
}
zip_file: dict[str, zipfile.ZipFile] = {
    'avatar': zipfile.ZipFile(DATA / 'avatar' / 'avatar.zip', 'w', zipfile.ZIP_STORED),
    'weapon': zipfile.ZipFile(DATA / 'weapon' / 'weapon.zip', 'w', zipfile.ZIP_STORED),
    'artifact': zipfile.ZipFile(DATA / 'artifact' / 'artifact.zip', 'w', zipfile.ZIP_STORED)
}

for type in json_data:
    for file in (DATA / type).iterdir():
        if file.suffix != '.json':
            continue
        zip_file[type].write(file, file.name)
        json_data[type].append(
            {
                'name': file.stem,
                'hash': hashlib.md5(file.read_bytes()).hexdigest()
            }
        )
for zip_ in zip_file.values():
    zip_.close()

json_data['data'] = []
data_zip = zipfile.ZipFile(DATA / 'data.zip', 'w', zipfile.ZIP_STORED)
for file in single_file:
    path = DATA / f'{file}.json'
    data_zip.write(path, path.name)
    json_data['data'].append(
        {
            'name': path.stem,
            'hash': hashlib.md5(path.read_bytes()).hexdigest()
        }
    )

data_zip.close()

save_json(json_data, DATA / 'data_list.json')




