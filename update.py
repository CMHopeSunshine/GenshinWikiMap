import time
import random
from path import *
from utils import load_json, save_json, get_describe_name, download_img
from AmbrApi.models import Character, Weapon, ELEMENT_MAP, Monster
from AmbrApi.data_source import ambr_requests, github_requests, download_from_ambr
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
    """更新基础数据"""
    if avatar_list := ambr_requests(AVATAR_LIST_API):
        save_json(avatar_list['items'], RAW / 'avatar_list.json')
        print('>>>角色列表raw更新完成')
    else:
        print('>>>角色列表raw更新失败')
    time.sleep(2)

    if avatar_detail := github_requests(
            'https://ghproxy.com/https://raw.githubusercontent.com/DGP-Studio/Snap.Metadata/main/Output/Avatar.json'):
        save_json(avatar_detail, RAW / 'Avatar.json')
        print('>>>角色信息raw更新完成')
    else:
        print('>>>角色信息raw更新失败')
    time.sleep(1)

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
    # if data := ambr_requests(属性Map_API):
    #     # 手动修正单手剑
    #     data.update({'WEAPON_SWORD_ONE_HAND': '单手剑'})
    #     save_json(data, DATA / '属性Map.json')
    #     print('>>>属性map更新完成')
    # else:
    #     print('>>>属性map更新失败')


def update_character():
    avatar_list = load_json(RAW / 'avatar_list.json')
    avatar_alias_file = load_json(DATA / '角色列表.json')
    type_file = load_json(DATA / '类型.json')
    weapon_type_data = load_json(DATA / '武器类型.json')
    prop_map = load_json(DATA / '属性Map.json')

    for avatar_id, avatar_data in avatar_list.items():
        if avatar_id.startswith(('10000005', '10000007')):
            continue
        ambr_data_file_path = AVATAR_RAW / f'{avatar_id}.json'
        map_img_path = CHARACTER_MAP_RESULT / f'{avatar_data["name"]}.jpg'

        need_update = False

        # 更新角色别名数据
        if avatar_id not in avatar_alias_file:
            avatar_alias_file[avatar_id] = [avatar_data['name']]

        # 更新类型数据
        weapon_type = prop_map[avatar_data['weaponType']]
        if avatar_data['name'] not in weapon_type_data:
            weapon_type_data[avatar_data['name']] = weapon_type
        if weapon_type not in type_file['角色']['武器类型']:
            type_file['角色']['武器类型'][weapon_type] = []
        if avatar_data['name'] not in type_file['角色']['武器类型'][weapon_type]:
            type_file['角色']['武器类型'][weapon_type].append(avatar_data['name'])
        element_type = ELEMENT_MAP[avatar_data['element']]
        if element_type not in type_file['角色']['元素类型']:
            type_file['角色']['元素类型'][element_type] = []
        if avatar_data['name'] not in type_file['角色']['元素类型'][element_type]:
            type_file['角色']['元素类型'][element_type].append(avatar_data['name'])

        if not map_img_path.exists():
            need_update = True
        if not ambr_data_file_path.exists():
            save_json(ambr_requests(AVATAR_INFO_API.format(avatar_id)), ambr_data_file_path)
            need_update = True
        elif avatar_data.get('beta'):
            new_data = ambr_requests(AVATAR_INFO_API.format(avatar_id))
            old_data = load_json(ambr_data_file_path)
            if new_data != old_data:
                need_update = True
                save_json(new_data, ambr_data_file_path)

        if need_update:
            draw_character_map(Character.parse_file(ambr_data_file_path))

    save_json(avatar_alias_file, DATA / '角色列表.json')
    save_json(weapon_type_data, DATA / '武器类型.json')
    save_json(type_file, DATA / '类型.json')

    avatar_detail_file = load_json(RAW / 'Avatar.json')
    region_data = load_json(DATA / '角色地区.json')
    for avatar_detail in avatar_detail_file:
        ambr_data = load_json(AVATAR_RAW / f"{avatar_detail['Id']}.json")
        save_file = DATA / 'avatar' / f"{avatar_detail['Id']}.json"
        if save_file.exists():
            avatar_info = load_json(save_file)
        else:
            avatar_info = {
                'id':            avatar_detail['Id'],
                'name':          avatar_detail['Name'],
                'element':       avatar_detail['FetterInfo']['VisionBefore'],
                'weapon':        weapon_type_data[avatar_detail['Name']],
                'rank':          avatar_detail['Quality'],
                'region':        region_data.get(avatar_detail['Name'], '未知'),
                'icon': {
                    'avatar': avatar_detail['Icon'],
                    'side': avatar_detail['SideIcon'],
                    'card': avatar_detail['Icon'] + '_Card',
                    'splash': avatar_detail['Icon'].replace('Icon', 'Img').replace('UI_', 'UI_Gacha_'),
                    'slice': avatar_detail['Icon'].replace('UI_', 'UI_Gacha_')
                },
                'property':      {},
                'talent':        {},
                'constellation': {}
            }
        if not (avatar_icon := RESOURCES / 'avatar' / f"{avatar_info['icon']['avatar']}.png").exists():
            download_from_ambr(avatar_icon)
        if not (avatar_side_icon := RESOURCES / 'avatar_side' / f"{avatar_info['icon']['side']}.png").exists():
            download_img(f"https://upload-bbs.mihoyo.com/game_record/genshin/character_side_icon/{avatar_info['icon']['side']}.png", avatar_side_icon)
        if not (avatar_splash_icon := RESOURCES / 'splash' / f"{avatar_info['icon']['splash']}.png").exists():
            download_from_ambr(avatar_splash_icon)
        avatar_info['property'] = [
            {
                'base':    ambr_data['upgrade']['prop'][0],
                'promote': [p['addProps']['FIGHT_PROP_BASE_HP']
                            for p in ambr_data['upgrade']['promote'][1:]
                            ]
            },
            {
                'base':    ambr_data['upgrade']['prop'][1],
                'promote': [p['addProps']['FIGHT_PROP_BASE_ATTACK']
                            for p in ambr_data['upgrade']['promote'][1:]
                            ]
            },
            {
                'base':    ambr_data['upgrade']['prop'][2],
                'promote': [p['addProps']['FIGHT_PROP_BASE_DEFENSE']
                            for p in ambr_data['upgrade']['promote'][1:]
                            ]
            },
            {
                'name': list(ambr_data['upgrade']['promote'][-1]['addProps'].keys())[-1],
                'promote': [
                    list(p['addProps'].values())[-1]
                    for p in ambr_data['upgrade']['promote'][1:]
                ]
            }
        ]

        for skill in avatar_detail['SkillDepot']['Skills']:
            avatar_info['talent'][str(skill['Id'])] = {
                'name': skill['Name'],
                'icon': skill['Icon']}
        avatar_info['talent'][str(avatar_detail['SkillDepot']['EnergySkill']['Id'])] = {
            'name': avatar_detail['SkillDepot']['EnergySkill']['Name'],
            'icon': avatar_detail['SkillDepot']['EnergySkill']['Icon']
        }
        for skill in avatar_detail['SkillDepot']['Inherents']:
            avatar_info['talent'][str(skill['Id'])] = {
                'name': skill['Name'],
                'icon': skill['Icon']}
        for c in avatar_detail['SkillDepot']['Talents']:
            avatar_info['constellation'][str(c['Id'])] = {
                'name': c['Name'],
                'icon': c['Icon']
            }
        c3_name = get_describe_name(avatar_detail['SkillDepot']['Talents'][2]['Description'])
        c5_name = get_describe_name(avatar_detail['SkillDepot']['Talents'][4]['Description'])
        avatar_info['talent_fix'] = {}
        if c3_name:
            for tid, t in avatar_info['talent'].items():
                if t['name'] == c3_name:
                    avatar_info['talent_fix'][tid] = t['name']
        if c5_name:
            for tid, t in avatar_info['talent'].items():
                if t['name'] == c5_name:
                    avatar_info['talent_fix'][tid] = t['name']
        if 'damage' not in avatar_info:
            avatar_info['damage'] = []
        if 'buff' not in avatar_info:
            avatar_info['buff'] = []
        save_json(avatar_info, save_file)


def update_material():
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


def update_weapon():
    """
    更新武器信息
    """
    weapon_list = load_json(RAW / 'weapon_list.json')
    prop_map = load_json(DATA / '属性Map.json')
    type_file = load_json(DATA / '类型.json')
    weapon_type_file = load_json(DATA / '武器类型.json')
    # weapon_info_file = load_json(DATA / '武器信息.json')
    weapon_list_file = load_json(DATA / '武器列表.json')
    for weapon_id, weapon_data in weapon_list.items():
        if not weapon_data['name']:
            continue
        if not (weapon_icon := RESOURCES / 'weapon' / f"{weapon_data['icon']}.png").exists():
            download_from_ambr(weapon_icon)
        data_save_path = DATA / 'weapon' / f'{weapon_id}.json'
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
        if need_update or not data_save_path.exists():
            weapon_info = Weapon.parse_file(save_path)
            dict_data = weapon_info.save_data()
            if data_save_path.exists():
                old_data = load_json(data_save_path)
                dict_data['buff'] = old_data['buff']
            else:
                dict_data['buff'] = []

            # weapon_info_file[weapon_id] = dict_data
            save_json(dict_data, data_save_path)

            # save_json(weapon_info_file, DATA / '武器信息.json')
    save_json(weapon_list_file, DATA / '武器列表.json')
    save_json(type_file, DATA / '类型.json')
    save_json(weapon_type_file, DATA / '武器类型.json')
    print('>>>[武器信息]全部更新完成')


def update_artifact():
    """
    更新圣遗物信息
    """
    suit_list = load_json(RAW / 'artifact_suit_list.json')
    artifact_info_file = load_json(DATA / '圣遗物信息.json')
    artifact_list_file = load_json(DATA / '圣遗物列表.json')
    # 遍历圣遗物列表
    for suit_id, suit_data in suit_list.items():
        # print(f'>>>>>>更新[{suit_data["name"]}]信息')
        suit_save_path = DATA / 'artifact' / f'{suit_id}.json'
        # 如果圣遗物别名列表中没有这个圣遗物套装，则添加进去
        if suit_data['name'] not in artifact_list_file:
            artifact_list_file[suit_data['name']] = [suit_data['name']]

        # 如果本地没有已下载的圣遗物套装raw数据，则下载，否则读取本地
        if not (save_path := ARTIFACT_RAW / f'{suit_id}.json').exists():
            suit_info = ambr_requests(ARTIFACT_INFO_API.format(suit_id))
            save_json(suit_info, save_path)
            time.sleep(1.5)
        else:
            suit_info = load_json(save_path)

        if suit_save_path.exists():
            suit_data = load_json(suit_save_path)
        else:
            suit_data = {
                'id': suit_id,
                'name': suit_info['name'],
                'short_name': suit_info['name'][:2],
                'level_list': suit_info['levelList'],
                'icon': suit_info['icon'],
                'part_list': {},
                'buff': []
            }

        # 遍历套装的圣遗物散件，如果没有散件数据，则添加进去
        for part_type, artifact in suit_info['suit'].items():
            artifact_icon = artifact['icon']
            if artifact_icon not in artifact_info_file:
                artifact_info_file[artifact_icon] = {
                    'name': artifact['name'],
                    'suit_id': suit_info['id'],
                    'suit_name': suit_info['name'],
                    'part': ARTIFACT_PART_MAP[part_type]
                }
            if artifact_icon not in suit_data['part_list']:
                suit_data['part_list'][artifact_icon] = {
                    'name': artifact['name'],
                    'part': ARTIFACT_PART_MAP[part_type]
                }
        save_json(suit_data, suit_save_path)
    save_json(artifact_list_file, DATA / '圣遗物列表.json')
    save_json(artifact_info_file, DATA / '圣遗物信息.json')
    print('>>>圣遗物信息更新完成')


def update_monster():
    """
    更新原魔信息
    """
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
            time.sleep(1)
            need_update = True
        elif monster_data.get('beta'):
            new_data = ambr_requests(MONSTER_INFO_API.format(monster_id))
            old_data = load_json(raw_data_file_path)
            if new_data != old_data:
                save_json(new_data, raw_data_file_path)
                need_update = True
            time.sleep(1)

        if need_update:
            monster_info = Monster.parse_file(raw_data_file_path)
            draw_monster_map(monster_info)

    save_json(monster_alias_list, DATA / '原魔列表.json')
