import re

from AmbrApi import Monster, download_from_ambr

from image_utils import PMImage, load_font
from utils import load_json
from path import *

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

title_font = load_font(FONT / 'SourceHanSerifCN-Bold.otf', 72)
description_font = load_font(FONT / 'SourceHanSansCN-Bold.otf', 30)
tap_font = load_font(FONT / 'SourceHanSerifCN-Bold.otf', 28)
prop_font = load_font(FONT / 'SourceHanSansCN-Bold.otf', 24)
prop_name_font = load_font(FONT / 'SourceHanSerifCN-Bold.otf', 24)

ignore_material = ['冒险阅历', '好感经验', '摩拉',
                   '坚牢黄玉', '哀叙冰玉', '自在松石',
                   '最胜紫晶', '生长碧翡', '涤净青金',
                   '燃愿玛瑙', '璀璨原钻', '精锻用魔矿',
                   '大英雄的经验']


def draw_monster_map(monster: Monster):
    if monster.type in ['禽鸟', '走兽', '游鱼', '其他']:
        return
    print(f'>>>>>>原魔[{monster.name}]图鉴 开始制作')
    img = PMImage(MONSTER_MAP_RESOURCES / '框贴图.png')
    # 名称
    img.text(monster.name, 620, 40, title_font, '#252525')
    # 描述
    monster.description = re.sub(r'<(.*)>', '\1', monster.description)
    img.text_box(monster.description.replace('\\n', '^').replace('^^', '^').strip('^'), (644, 1418),
                 (295, 568), description_font, '#252525')
    # 立绘
    icon = download_from_ambr(RESOURCES / 'monster' / f'{monster.icon}.png')
    icon = icon.resize((492, 492))
    img.paste(icon, (74, 71))

    # taps
    taps = [monster.title, monster.specialName, monster.type]
    now_tap_width = 620
    for tap in taps:
        if tap:
            type_length = tap_font.getlength(tap)
            if now_tap_width + type_length >= 1490:
                break
            img.draw_rounded_rectangle((now_tap_width, 142, now_tap_width + type_length + 10, 191), 10, '#ff6f30')
            img.text(tap, (now_tap_width, now_tap_width + type_length + 10), (140, 189), tap_font, 'white', 'center')
            now_tap_width += type_length + 10 + 15

    monster_detail = None
    if monster.name == '「公子」':
        monster_detail = monster.entries['29030106']
    else:
        for entry in monster.entries.values():
            if entry.reward is not None:
                monster_detail = entry
                break
        if not monster_detail:
            monster_detail = list(monster.entries.values())[0]

    # 详细属性
    img.text('各等级属性详情', (68, 475), 733, prop_name_font, '#252525', 'center')
    for i in range(5):
        level = str(60 + 10 * i)
        img.text(level, (78, 124), 793 + i * 47, prop_font, '#252525', 'center')

        health = monster_detail.get_health_num(level)
        health_str = f'{round(health / 10000, 1)}W' if health >= 10000 else f'{round(health / 1000, 1)}K'
        img.text(health_str, (170, 237), 793 + i * 47, prop_font, '#252525', 'center')

        attack = monster_detail.get_attack_num(level)
        img.text(str(attack), (283, 349), 793 + i * 47, prop_font, '#252525', 'center')

        defense = monster_detail.get_defense_num(level)
        img.text(str(defense), (396, 460), 793 + i * 47, prop_font, '#252525', 'center')

    # 抗性
    img.text('正常状态', 534, 790, description_font, '#252525')
    if res := monster_detail.resistance:
    # 火
        res_str = f'{int(res.fireSubHurt * 100)}%' if monster.name not in ['火史莱姆', '大型火史莱姆', '火飘浮灵', '无相之火'] else '免疫'
        img.text(res_str, (677, 741), 790, description_font, '#252525')
        # 水
        res_str = f'{int(res.waterSubHurt * 100)}%' if monster.name not in ['水史莱姆', '大型水史莱姆', '水飘浮灵', '无相之水', '纯水精灵'] else '免疫'
        img.text(res_str, (773, 837), 790, description_font, '#252525')
        # 风
        res_str = f'{int(res.windSubHurt * 100)}%' if monster.name not in ['风史莱姆', '大型风史莱姆', '风飘浮灵', '无相之风', '北风的王狼，奔狼的领主'] else '免疫'
        img.text(res_str, (869, 933), 790, description_font, '#252525')
        # 雷
        res_str = f'{int(res.elecSubHurt * 100)}%' if monster.name not in ['雷史莱姆', '大型雷史莱姆', '变异雷史莱姆', '雷飘浮灵', '无相之雷', '雷音权现'] else '免疫'
        img.text(res_str, (965, 1029), 790, description_font, '#252525')
        # 草
        res_str = f'{int(res.grassSubHurt * 100)}%' if monster.name not in ['草史莱姆', '大型草史莱姆', '草飘浮灵', '无相之草'] else '免疫'
        img.text(res_str, (1062, 1126), 790, description_font, '#252525')
        # 冰
        res_str = f'{int(res.iceSubHurt * 100)}%' if monster.name not in ['冰史莱姆', '大型冰史莱姆', '冰飘浮灵', '无相之冰', '北风的王狼，奔狼的领主'] else '免疫'
        img.text(res_str, (1157, 1221), 790, description_font, '#252525')
        # 岩
        res_str = f'{int(res.rockSubHurt * 100)}%' if monster.name not in ['岩史莱姆', '大型岩史莱姆', '岩飘浮灵', '无相之岩'] else '免疫'
        img.text(res_str, (1253, 1317), 790, description_font, '#252525')
        # 物理
        img.text(f'{int(res.physicalSubHurt * 100)}%', (1349, 1413), 790, description_font, '#252525')
    

    if monster_detail.reward:
        materials = monster_detail.get_material_group()
        materials = [material for material in materials
                     if material['name'] not in ignore_material and
                     not material['name'].endswith('原胚')]
        if materials:
            img.stretch((1134 + 20, 1713 - 20), len(materials * 190) - 40, 'height')
            material_info = load_json(DATA / '材料列表.json')

            for i, material in enumerate(materials):
                img.paste(CHARACTER_MAP_RESOURCES / '圆框.png', (81, 1190 + i * 181))
                img.text(material['name'], (81, 201), 1155 + i * 181, prop_name_font, '#252525', 'center')
                material_icon = download_from_ambr(MATERIALS / f'{material["icon"]}.png')
                material_icon = material_icon.resize((100, 100))
                img.paste(material_icon, (94, 1200 + i * 181))
                if material['name'] not in material_info:
                    charas = []
                else:
                    charas = material_info[material['name']]['适用角色']
                if charas:
                    if '旅行者' in charas:
                        charas.remove('旅行者')
                        charas.append('荧')
                    if len(charas) > 8:
                        charas = charas[:8]
                    for j, chara in enumerate(charas):
                        img.paste(CHARACTER_MAP_RESOURCES / '圆框橙.png', (258 + j * 148, 1172 + i * 181))
                        chara_icon = PMImage(RESOURCES / 'avatar_new' / f'{chara}.png')
                        chara_icon.resize((116, 116))
                        chara_icon.to_circle('circle')
                        img.paste(chara_icon, (262 + j * 148, 1176 + i * 181))
                        img.draw_rounded_rectangle((265 + j * 148, 1267 + i * 181, 265 + j * 148 + 113, 1267 + i * 181 + 30), 5, '#ff6f30')
                        img.text(chara, (265 + j * 148, 265 + j * 148 + 113), 1263 + i * 181, prop_name_font, 'white', 'center')
        total_height = img.height
    else:
        img.crop((0, 0, img.height, 1055))
        total_height = img.height + 50
    bg_img = PMImage(CHARACTER_MAP_RESOURCES / '背景色.png')
    bg_img.resize((1510, total_height))
    border_img = PMImage(CHARACTER_MAP_RESOURCES / '边框.png')
    border_img.stretch((50, border_img.height - 50), total_height - 100, 'height')
    border_img.stretch((50, border_img.width - 50), 1410, 'width')
    bg_img.paste(border_img, (0, 0))
    bg_img.covered(ICON / '方块纹理.png')
    bg_img.paste(img, (0, 0))
    bg_img.text('制作：西北一枝花&惜月', bg_img.width - 50, bg_img.height - 37, prop_name_font, '#252525', 'right')
    bg_img.convert('RGB')
    bg_img.save(MONSTER_MAP_RESULT / f'{monster.name}.jpg', mode='JPEG', quality=60)
    print(f'>>>>>>原魔[{monster.name}]图鉴 制作完成')
    # bg_img.show()


if __name__ == '__main__':
    monster_ = Monster.parse_file(MONSTER_RAW / '29020101.json')
    draw_monster_map(monster_)
