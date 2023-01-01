import time
import random
from path import *
from utils import load_json, save_json
from AmbrApi.models import Character, Weapon, ELEMENT_MAP, Monster
from AmbrApi.data_source import ambr_requests
from AmbrApi.api import *

from draw_character_map import draw_character_map
from draw_monster_map import draw_monster_map

ARTIFACT_PART_MAP = {
    'EQUIP_BRACER':   '生之花',
    'EQUIP_NECKLACE': '死之羽',
    'EQUIP_SHOES':    '时之沙',
    'EQUIP_RING':     '空之杯',
    'EQUIP_DRESS':    '理之冠'
}


def update_constant():
    if avatar_list := ambr_requests(AVATAR_LIST_API):
        save_json(avatar_list['items'], RAW / 'avatar_list.json')
        print('>>>角色列表raw更新完成')
    else:
        print('>>>角色列表raw更新失败')
    time.sleep(2)

    if material_list := ambr_requests(MATERIAL_LIST_API):
        save_json(material_list, RAW / 'materials.json')
        print('>>>材料列表raw更新完成')
    else:
        print('>>>材料列表raw更新失败')
    time.sleep(2)

    if weapon_list := ambr_requests(WEAPON_LIST_API):
        save_json(weapon_list['items'], RAW / 'weapon_list.json')
        print('>>>武器列表raw更新完成')
    else:
        print('>>>武器列表raw更新失败')
    time.sleep(2)

    if artifact_suit_list := ambr_requests(ARTIFACT_LIST_API):
        save_json(artifact_suit_list['items'], RAW / 'artifact_suit_list.json')
        print('>>>圣遗物套装列表raw更新完成')
    else:
        print('>>>圣遗物套装列表raw更新失败')
    time.sleep(2)

    # # 更新角色曲线
    # if data := ambr_requests(AVATAR_CURVE_API):
    #     save_json(data, RAW / 'avatar_curve.json')
    #     print('>>>角色曲线raw更新完成')
    # else:
    #     print('>>>角色曲线raw更新失败')
    # time.sleep(2)
    # # 更新武器曲线
    # if data := ambr_requests(WEAPON_CURVE_API):
    #     save_json(data, RAW / 'weapon_curve.json')
    #     print('>>>武器曲线raw更新完成')
    # else:
    #     print('>>>武器曲线raw更新失败')
    # time.sleep(2)
    # # 更新属性map
    # if data := ambr_requests(PROP_MAP_API):
    #     # 手动修正单手剑
    #     data.update({'WEAPON_SWORD_ONE_HAND': '单手剑'})
    #     save_json(data, RAW / 'prop_map.json')
    #     print('>>>属性map更新完成')
    # else:
    #     print('>>>属性map更新失败')


def update_characters():
    avatar_list = load_json(RAW / 'avatar_list.json')
    avatar_info_file = load_json(DATA / '角色信息.json')

    for avatar_id, avatar_data in avatar_list.items():
        raw_data_file_path = AVATAR_RAW / f'{avatar_id}.json'
        map_img_path = CHARACTER_MAP_RESULT / f'{avatar_data["name"]}.jpg'

        need_update = False
        if not map_img_path.exists():
            need_update = True
        if not raw_data_file_path.exists():
            save_json(ambr_requests(AVATAR_INFO_API.format(avatar_id)), raw_data_file_path)
            need_update = True
        elif avatar_data['beta']:
            new_data = ambr_requests(AVATAR_INFO_API.format(avatar_id))
            old_data = load_json(raw_data_file_path)
            if new_data != old_data:
                need_update = True
                save_json(new_data, raw_data_file_path)

        if need_update:
            avatar_info = Character.parse_file(raw_data_file_path)
            draw_character_map(avatar_info)

    # new_avatar_list = ambr_requests(AVATAR_LIST_API)['items']
    # old_avatar_list = load_json(RAW / 'avatar_list.json')
    #
    # # 尚未制作的角色
    # need_update = [avatar_id for avatar_id in new_avatar_list if
    #                not (CHARACTER_MAP_RESULT_RAW / f'{avatar_id}.png').exists()]
    #
    # # 新角色
    # need_update.extend([i for i in new_avatar_list if i not in old_avatar_list])
    # # 角色信息有更新
    # for character_id in new_avatar_list:
    #     if '-' in character_id or int(character_id) <= 10000076:  # 艾尔海森
    #         continue
    #     data = ambr_requests(AVATAR_INFO_API.format(character_id))
    #     if not (AVATAR_RAW / f'{character_id}.json').exists():
    #         need_update.append(character_id)
    #     if data != load_json(AVATAR_RAW / f'{character_id}.json'):
    #         need_update.append(character_id)
    #     save_json(data, AVATAR_RAW / f'{character_id}.json')
    #     print(f'>>>>>>{character_id}角色信息更新完成')
    #     time.sleep(random.uniform(0.5, 1.5))
    # # 保存新的角色列表
    # save_json(new_avatar_list, RAW / 'avatar_list.json')
    # print('>>>角色信息及列表更新完成')
    # # 角色立绘偏移有更新
    # paint_offset = load_json(DATA / '角色立绘偏移.json')
    # paint_offset_done = load_json(DATA / '角色立绘偏移已用.json')
    # for avatar_id, offset in paint_offset.items():
    #     if avatar_id not in paint_offset_done or offset != paint_offset_done[avatar_id]:
    #         need_update.append(avatar_id)
    # # 保存新的角色立绘偏移
    # save_json(paint_offset, DATA / '角色立绘偏移已用.json')
    # print('>>>角色立绘偏移更新完成')
    #
    # need_update = list(set(need_update))
    # print(f'>>>>>>共有 {len(need_update)} 个角色图鉴需要更新')
    #
    # return need_update


def update_material_info():
    """
    更新材料信息
    """
    material_dict: dict[str, dict] = {item['name']: {'id':     item['id'],
                                                     '名称':   item['name'],
                                                     '稀有度': item['rank'],
                                                     '图标':   item['icon'],
                                                     } for item in load_json(RAW / 'materials.json')['items'].values()}
    avatar_infos = [Character.parse_file(AVATAR_RAW / f'{avatar_id}.json') for avatar_id in
                    load_json(RAW / 'avatar_list.json')]
    avatar_materials: dict[str, list[int]] = {avatar.name: avatar.get_material_ids() for avatar in avatar_infos}
    for material in material_dict.values():
        if (MATERIAL_RAW / f'{material["id"]}.json').exists():
            material_info = load_json(MATERIAL_RAW / f'{material["id"]}.json')
        else:
            print(f'>>>>>>获取 {material["id"]} 材料信息')
            material_info = ambr_requests(MATERIAL_INFO_API.format(material['id']))
            save_json(material_info, MATERIAL_RAW / f'{material["id"]}.json')
            time.sleep(random.randint(1, 2))
        material['描述'] = material_info['description']
        material['类型'] = material_info['type']
        if material_info.get('source'):
            material['获取途径'] = [p['name'] for p in material_info['source']]  # type: ignore
        material['适用角色'] = [name for name, mats in avatar_materials.items() if material['id'] in mats]
    save_json(material_dict, DATA / '材料列表.json')
    print('>>>材料列表更新完成')


def update_weapon_info():
    """
    更新武器信息
    """
    weapon_list = load_json(RAW / 'weapon_list.json')
    prop_map = load_json(RAW / 'prop_map.json')
    type_file = load_json(DATA / '物品类型.json')
    weapon_type_file = load_json(DATA / '武器类型.json')
    weapon_info_file = load_json(DATA / '武器信息.json')
    weapon_list_file = load_json(DATA / '武器列表.json')
    for weapon_id, weapon_data in weapon_list.items():
        if not weapon_data['name']:
            continue
        # 如果本地没有已下载的武器raw数据，则下载，否则读取本地
        if not (save_path := WEAPON_RAW / f'{weapon_id}.json').exists() or weapon_data.get('beta'):
            weapon_data = ambr_requests(WEAPON_INFO_API.format(weapon_id))
            save_json(weapon_data, save_path)
            time.sleep(1.5)
            need_update = True
        else:
            need_update = False
        if weapon_data['name'] not in weapon_list_file:
            weapon_list_file[weapon_data['name']] = [weapon_data['name']]

        weapon_type = weapon_data['type'] if weapon_data['type'] in {'单手剑', '双手剑', '长柄武器', '法器', '弓'} else \
            prop_map[weapon_data['type']]
        if weapon_data['name'] not in weapon_type_file:
            weapon_type_file[weapon_data['name']] = weapon_type
        if weapon_type not in type_file['武器']:
            type_file['武器'][weapon_type] = []
        if weapon_data['name'] not in type_file['武器'][weapon_type]:
            type_file['武器'][weapon_type].append(weapon_data['name'])

        # 如果没有这个武器的详细信息，或者需要更新，则更新
        if need_update or weapon_id not in weapon_info_file:
            weapon_info = Weapon.parse_file(save_path)
            dict_data = weapon_info.save_to_dict()
            weapon_info_file[weapon_id] = dict_data
            print(f'>>>>>>{weapon_info.name} 武器信息更新完成')

            save_json(weapon_info_file, DATA / '武器信息.json')
    save_json(weapon_list_file, DATA / '武器列表.json')
    save_json(type_file, DATA / '物品类型.json')
    save_json(weapon_type_file, DATA / '物品武器类型.json')
    print('>>>武器信息全部更新完成')


def update_artifact_info():
    """
    更新圣遗物信息
    """
    suit_list = load_json(RAW / 'artifact_suit_list.json')
    artifact_info_file = load_json(DATA / '圣遗物信息.json')
    artifact_list_file = load_json(DATA / '圣遗物列表.json')
    artifact_suit_file = load_json(DATA / '圣遗物套装信息.json')
    # 遍历圣遗物列表
    for suit_id in suit_list.keys():
        # 如果本地没有已下载的圣遗物套装raw数据，则下载，否则读取本地
        if not (save_path := ARTIFACT_RAW / f'{suit_id}.json').exists():
            suit_info = ambr_requests(ARTIFACT_INFO_API.format(suit_id))
            save_json(suit_info, save_path)
            time.sleep(1.5)
            update_flag = True
        else:
            suit_info = load_json(save_path)
            update_flag = False

        # 如果圣遗物别名列表中没有这个圣遗物套装，则添加进去
        if suit_info['name'] not in artifact_list_file:
            artifact_list_file[suit_info['name']] = [suit_info['name']]

        # 如果没有这个圣遗物套装的详细信息，或者需要更新，则更新
        if update_flag or suit_id not in artifact_suit_file:
            if len(suit_info['affixList']) == 1:
                effect = {
                    '单件': list(suit_info['affixList'].values())[0]
                }
            else:
                effect = {
                    '两件套': list(suit_info['affixList'].values())[0],
                    '四件套': list(suit_info['affixList'].values())[1]
                }
            artifact_suit_file[suit_id] = {
                'id':       suit_id,
                '名称':     suit_info['name'],
                '等级列表': suit_info['levelList'],
                '效果':     effect,
                '图标':     suit_info['icon'],
                '散件列表': []
            }

        # 遍历套装的圣遗物散件，如果没有散件数据，则添加进去
        for part_type, artifact in suit_info['suit'].items():
            artifact_id = artifact['icon'].replace('UI_RelicIcon_')
            if artifact_id not in artifact_info_file:
                artifact_info_file[artifact_id] = {
                    '名称': artifact['name'],
                    '描述': artifact['description'],
                    '套装': {
                        'id':   suit_info['id'],
                        '名称': suit_info['name']
                    },
                    '部位': ARTIFACT_PART_MAP[part_type],
                    '图标': artifact['icon']
                }
            if artifact_id not in artifact_suit_file[suit_id]['散件列表']:
                artifact_suit_file[suit_id]['散件列表'].append(artifact_id)
    save_json(artifact_list_file, DATA / '圣遗物列表.json')
    save_json(artifact_info_file, DATA / '圣遗物信息.json')
    save_json(artifact_suit_file, DATA / '圣遗物套装信息.json')
    print('>>>圣遗物信息更新完成')


def update_type_info():
    """
    更新类型信息
    """
    type_file = load_json(DATA / '物品类型.json')
    weapon_type_file = load_json(DATA / '武器类型.json')
    avatar_list = load_json(RAW / 'avatar_list.json')
    prop_map = load_json(RAW / 'prop_map.json')
    if '角色' not in type_file:
        type_file['角色'] = {}
    if '武器类型' not in type_file['角色']:
        type_file['角色']['武器类型'] = {}
    if '元素类型' not in type_file['角色']:
        type_file['角色']['元素类型'] = {}
    for avatar in avatar_list.values():
        weapon_type = prop_map[avatar['weaponType']]
        if weapon_type not in type_file['角色']['武器类型']:
            type_file['角色']['武器类型'][weapon_type] = []
        if avatar['name'] not in type_file['角色']['武器类型'][weapon_type]:
            type_file['角色']['武器类型'][weapon_type].append(avatar['name'])
        if avatar['name'] not in weapon_type_file:
            weapon_type_file[avatar['name']] = weapon_type

        element_type = ELEMENT_MAP[avatar['element']]
        if element_type not in type_file['角色']['元素类型']:
            type_file['角色']['元素类型'][element_type] = []
        if avatar['name'] not in type_file['角色']['元素类型'][element_type]:
            type_file['角色']['元素类型'][element_type].append(avatar['name'])

    if '武器' not in type_file:
        type_file['武器'] = {}
    weapon_list = load_json(RAW / 'weapon_list.json')
    for weapon in weapon_list.values():
        if not weapon['name']:
            continue
        weapon_type = prop_map[weapon['type']]
        if weapon_type not in type_file['武器']:
            type_file['武器'][weapon_type] = []
        if weapon['name'] not in type_file['武器'][weapon_type]:
            type_file['武器'][weapon_type].append(weapon['name'])
        if weapon['name'] not in weapon_type_file:
            weapon_type_file[weapon['name']] = weapon_type

    save_json(type_file, DATA / '物品类型.json')
    save_json(weapon_type_file, DATA / '物品武器类型.json')

    print('>>>物品类型信息更新完成')


def update_monster_info():
    monster_list = load_json(RAW / 'monster_list.json')
    monster_alias_list = load_json(DATA / '原魔列表.json')

    for monster_id, monster_data in monster_list.items():
        if monster_data['type'] in ['AVIARY', 'ANIMAL', 'FISH', 'CRITTER']:
            continue
        raw_data_file_path = MONSTER_RAW / f'{monster_id}.json'
        map_img_path = MONSTER_MAP_RESULT / f"{monster_data['name']}.jpg"
        if monster_data['name'] not in monster_alias_list:
            monster_alias_list[monster_data['name']] = [monster_data['name']]

        need_update = False
        if not map_img_path.exists():
            need_update = True
        if not raw_data_file_path.exists():
            save_json(ambr_requests(MONSTER_INFO_API.format(monster_id)), raw_data_file_path)
            time.sleep(1.5)
            need_update = True
        # elif monster_data.get('beta'):
        #     new_data = ambr_requests(MONSTER_INFO_API.format(monster_id))
        #     old_data = load_json(raw_data_file_path)
        #     if new_data != old_data:
        #         save_json(new_data, raw_data_file_path)
        #         need_update = True
        #     time.sleep(1.5)

        if need_update:
            monster_info = Monster.parse_file(raw_data_file_path)
            draw_monster_map(monster_info)

    save_json(monster_alias_list, DATA / '原魔列表.json')
