import zipfile
import hashlib

from path import DATA
from utils import save_json


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
        if file.suffix == '.zip':
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
save_json(json_data, DATA / 'data_list.json')




