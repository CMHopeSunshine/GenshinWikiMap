import time
import random
from path import CHARACTER_MAP_RESULT_RAW, RAW, AVATAR_RAW, MATERIAL_RAW, DATA
from utils import load_json, save_json
from .models import Character
from .data_source import get_avatar_info, get_avatar_list, get_avatar_curve, \
    get_weapon_curve, get_material_list, get_prop_map, get_material_info


def update_constant():
    # 更新材料列表
    if data := get_material_list():
        save_json(data, RAW / 'materials.json')
        print('>>>材料列表raw更新完成')
    else:
        print('>>>材料列表raw更新失败')
    time.sleep(2)
    # # 更新角色曲线
    # if data := get_avatar_curve():
    #     save_json(data, RAW / 'avatar_curve.json')
    #     print('>>>角色曲线raw更新完成')
    # else:
    #     print('>>>角色曲线raw更新失败')
    # time.sleep(2)
    # # 更新武器曲线
    # if data := get_weapon_curve():
    #     save_json(data, RAW / 'weapon_curve.json')
    #     print('>>>武器曲线raw更新完成')
    # else:
    #     print(>>>武器曲线raw更新失败')
    # time.sleep(2)
    # 更新属性map
    # if data := get_prop_map():
    #     # 手动修正单手剑
    #     data.update({'WEAPON_SWORD_ONE_HAND': '单手剑'})
    #     save_json(data, RAW / 'prop_map.json')
    #     print('>>>属性map更新完成')
    # else:
    #     print('>>>属性map更新失败')


def get_update_characters_map() -> list[str]:
    new_avatar_list = load_json(RAW / 'avatar_list.json')
    return [avatar_id for avatar_id in new_avatar_list if not (CHARACTER_MAP_RESULT_RAW / f'{avatar_id}.png').exists()]
    # return list(new_avatar_list.keys())
    new_avatar_list = get_avatar_list()
    old_avatar_list = load_json(RAW / 'avatar_list.json')

    # 尚未制作的角色
    need_update = [avatar_id for avatar_id in new_avatar_list if
                   not (CHARACTER_MAP_RESULT_RAW / f'{avatar_id}.png').exists()]

    # 新角色
    need_update.extend([i for i in new_avatar_list if i not in old_avatar_list])
    # 角色信息有更新
    for character_id in new_avatar_list:
        if '-' in character_id or int(character_id) <= 10000074:  # 莱依拉
            continue
        data = get_avatar_info(character_id)
        if not (AVATAR_RAW / f'{character_id}.json').exists():
            need_update.append(character_id)
        if data != load_json(AVATAR_RAW / f'{character_id}.json'):
            need_update.append(character_id)
        save_json(data, AVATAR_RAW / f'{character_id}.json')
        print(f'>>>>>>{character_id}角色信息更新完成')
        time.sleep(random.uniform(0.5, 1.5))
    # 保存新的角色列表
    save_json(new_avatar_list, RAW / 'avatar_list.json')
    print('>>>角色信息及列表更新完成')
    # 角色立绘偏移有更新
    paint_offset = load_json(DATA / 'paint_offset.json')
    paint_offset_done = load_json(DATA / 'paint_offset_done.json')
    for avatar_id, offset in paint_offset.items():
        if avatar_id not in paint_offset_done or offset != paint_offset_done[avatar_id]:
            need_update.append(avatar_id)
    # 保存新的角色立绘偏移
    save_json(paint_offset, DATA / 'paint_offset_done.json')
    print('>>>角色立绘偏移更新完成')

    need_update = list(set(need_update))
    print(f'>>>>>>共有 {len(need_update)} 个角色图鉴需要更新')

    return need_update


def update_material_need():
    material_dict: dict[str, dict] = {item['name']: {'id':     item['id'],
                                                     '名称':   item['name'],
                                                     '稀有度': item['rank'],
                                                     '图标':   item['icon'],
                                                     } for item in load_json(RAW / 'materials.json')['items'].values()}
    avatar_infos = [Character.parse_file(AVATAR_RAW / f'{avatar_id}.json') for avatar_id in load_json(RAW / 'avatar_list.json')]
    avatar_materials: dict[str, list[int]] = {avatar.name: avatar.get_material_ids() for avatar in avatar_infos}
    for material in material_dict.values():
        if (MATERIAL_RAW / f'{material["id"]}.json').exists():
            material_info = load_json(MATERIAL_RAW / f'{material["id"]}.json')
        else:
            print(f'>>>>>>获取 {material["id"]} 材料信息')
            material_info = get_material_info(material['id'])
            save_json(material_info, MATERIAL_RAW / f'{material["id"]}.json')
            time.sleep(random.randint(1, 2))
        material['描述'] = material_info['description']
        material['类型'] = material_info['type']
        if material_info.get('source'):
            material['获取途径'] = [p['name'] for p in material_info['source']]
        material['适用角色'] = [name for name, mats in avatar_materials.items() if material['id'] in mats]
    save_json(material_dict, DATA / '材料列表.json')
    print('>>>材料列表更新完成')

