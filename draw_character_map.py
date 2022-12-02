import re
from AmbrApi import Character, Talent, Constellation, download_from_ambr

from image_utils import PMImage, load_font
from utils import load_json
from path import *

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

title_font = load_font(FONT / 'SourceHanSerifCN-Bold.otf', 72)
prop_name_font = load_font(FONT / 'SourceHanSansCN-Bold.otf', 30)
prop_value_font = load_font(FONT / 'bahnschrift_regular.ttf', 48, 'Regular')
main_text_font = load_font(FONT / 'SourceHanSansCN-Bold.otf', 22)
talent_data_font = load_font(FONT / 'SourceHanSansCN-Bold.otf', 24)
constellation_name_font = load_font(FONT / 'SourceHanSansCN-Bold.otf', 30)


# 文字颜色，暂未实现
# Char = TypedDict('Char', {'name': str, 'color': str})


# def color_text(text: str) -> list[Char]:
#     text_list = []
#     colorful_texts = re.findall(r'<color=(.*?)>(.*?)</color>', text)
#     for colorful_text in colorful_texts:
#         # colorful_text[0]在text的位置
#
#     # for i in re.finditer(r'<color=#([0-9a-fA-F]{6})>(.*?)</color>', text):
#     #     text_list.append({'name': i.group(2), 'color': i.group(1)})
#     return text_list


def draw_talent(talent: Talent, index: int, chara_name: str) -> PMImage:
    # sourcery skip: simplify-numeric-comparison
    # 宽度882，两边空21，可用区域840
    img = PMImage(size=(882, 2500), mode='RGBA', color=(255, 255, 255, 0))
    # ----------图标----------
    img.paste(CHARACTER_MAP_RESOURCES / '圆框橙.png', (35, 5))
    talent_icon = download_from_ambr(TALENT / f'{talent.icon}.png')
    talent_icon = talent_icon.resize((100, 100))
    img.paste(talent_icon, (48, 15))
    if chara_name in {'神里绫华', '莫娜'} and index >= 4:
        index -= 1
    if index not in [2, 6, 8]:
        img.paste(CHARACTER_MAP_RESOURCES / '点.png', (27, 0))
    if index == 0:
        img.text('A', 39, 5, constellation_name_font, 'white')
    elif index == 1:
        img.text('E', 39, 5, constellation_name_font, 'white')
    elif index == 3:
        img.text('Q', 37, 5, constellation_name_font, 'white')
    elif index == 4:
        if talent.name == '神里流·霜灭':
            img.text('Q', 37, 5, constellation_name_font, 'white')
        else:
            img.text('20', 30, 5, constellation_name_font, 'white')
    elif index == 5:
        img.text('60', 30, 5, constellation_name_font, 'white')
    talent_name_length = talent_data_font.getlength(talent.name.strip('普通攻击·'))
    left = 97 - talent_name_length / 2 - 5
    right = 97 + talent_name_length / 2 + 5
    img.draw_rounded_rectangle((left, 100, right, 100 + 38), 5, '#ff6f30')
    img.text(talent.name.strip('普通攻击·'), (left, right), (100, 100 + 38), talent_data_font, 'white', 'center')
    # ----------图标----------

    # ----------描述----------
    now_height = 0
    text = re.sub(r'<.*?>', '', talent.description.replace('\\n', '^')).strip('^')
    if len(text) <= 40:
        description_length = img.text_box(text, (200, 840), (now_height + 20, now_height + 1000), main_text_font,
                                          '#252525')
    else:
        description_length = img.text_box(text, (200, 840), (now_height, now_height + 1000), main_text_font, '#252525')
    now_height += description_length
    # ----------描述----------

    # ----------倍率----------
    this_width = 200
    if promote_data := talent.get_promote_list():
        now_height += 20
        for name, value in promote_data.items():
            promote_text = f'{name}  {value[8] if len(value) > 8 else value[0]}'
            promote_text_size = talent_data_font.getsize(promote_text)
            if this_width + promote_text_size[0] + 10 + 10 > 862:
                this_width = 200
                now_height += 41
            img.draw_rounded_rectangle(
                (this_width, now_height, this_width + promote_text_size[0] + 10, now_height + 36), 5, '#ff6f30')
            img.text(promote_text, this_width + 5, (now_height, now_height + 36), talent_data_font, 'white', 'center')
            this_width += promote_text_size[0] + 10 + 10
        now_height += 41
    # ----------倍率----------
    now_height = max(now_height, 157)
    img.crop((0, 0, 882, now_height))
    return img


def draw_constellation(constellation: Constellation):
    # 宽度562，两边空21，可用区域520
    img = PMImage(size=(562, 1200), mode='RGBA', color=(255, 255, 255, 0))
    # ----------图标----------
    img.paste(CHARACTER_MAP_RESOURCES / '圆框橙.png', (35, 5))
    constellation_icon = download_from_ambr(CONSTELLATION / f'{constellation.icon}.png')
    constellation_icon.resize((78, 78))
    img.paste(constellation_icon, (48, 15))
    # ----------图标----------
    now_height = 0
    img.text(constellation.name, 200, now_height, constellation_name_font, '#df5d25')
    now_height += 38
    text = re.sub(r'<.*?>', '', constellation.description.replace('\\n', '^')).strip('^')
    description_length = img.text_box(text, (200, 520), (now_height, now_height + 1000), main_text_font, '#252525')
    now_height += description_length + 30
    now_height = max(now_height, 127)
    img.crop((0, 0, 562, now_height))
    return img


def draw_character_map(chara: Character):
    print(f'>>>>>>角色[{chara.name}]图鉴 开始制作')
    img = PMImage(CHARACTER_MAP_RESOURCES / '框贴图.png')
    # 元素图标
    img.paste(ICON / f'{chara.element}.png', (621, 40))
    # 星级图标
    img.paste(ICON / f'{chara.rank}star.png', (696, 45))
    # 是否测试角色
    if chara.beta:
        img.text('测试角色', 950 if chara.rank == 5 else 900, 64, main_text_font, '#252525')
    # 角色名称标题
    img.text(chara.title_name, 573, 83, title_font, '#252525')
    # ---------------立绘---------------
    offset = load_json(DATA / 'paint_offset_done.json').get(chara.id, [0, 0])
    gacha_img = download_from_ambr(GACHA_IMG / f'UI_Gacha_AvatarImg_{chara.icon.split("_")[-1]}.png')
    img.paste(CHARACTER_MAP_RESOURCES / '立绘下花纹.png', (35, 40))
    gacha_img = gacha_img.crop((gacha_img.width // 2 - 250 + offset[0],
                                gacha_img.height // 2 - 250 - 100 + offset[1],
                                gacha_img.width // 2 + 250 + offset[0],
                                gacha_img.height // 2 + 250 - 100 + offset[1]))
    img.paste(gacha_img, (65, 75))
    img.paste(CHARACTER_MAP_RESOURCES / '立绘上花纹.png', (35, 40))
    # ---------------立绘---------------
    # ---------------基础数据---------------
    # 属性名间隙
    hp_length = img.text_length('基础生命', prop_name_font)
    atk_length = img.text_length('基础攻击', prop_name_font)
    def_length = img.text_length('基础防御', prop_name_font)
    ext_length = img.text_length(chara.extra_prop_name, prop_name_font)
    bir_length = img.text_length('生日', prop_name_font)
    clearance = int((800 - (hp_length + atk_length + def_length + ext_length + bir_length)) / 4)
    now_width = 660
    # 生命值
    img.text('基础生命', now_width, 268, prop_name_font, '#252525')
    img.text(str(chara.health), (now_width, now_width + hp_length), 308, prop_value_font, '#252525', 'center')
    now_width += hp_length + clearance
    # 攻击
    img.text('基础攻击', now_width, 268, prop_name_font, '#252525')
    img.text(str(chara.attack), (now_width, now_width + atk_length), 308, prop_value_font, '#252525', 'center')
    now_width += atk_length + clearance
    # 防御
    img.text('基础防御', now_width, 268, prop_name_font, '#252525')
    img.text(str(chara.defense), (now_width, now_width + def_length), 308, prop_value_font, '#252525', 'center')
    now_width += def_length + clearance
    # 突破
    img.text(chara.extra_prop_name, now_width, 268, prop_name_font, '#252525')
    if chara.extra_prop_name == '元素精通':
        extra_prop_value_str = str(chara.extra_prop_value)
    else:
        extra_prop_value_str = f'{round(chara.extra_prop_value * 100, 1)}%'
    img.text(extra_prop_value_str, (now_width, now_width + ext_length), 308, prop_value_font, '#252525', 'center')
    img.paste(ICON / '突破.png', (now_width + ext_length - 5, 258))
    now_width += ext_length + clearance
    # 生日
    img.text('生日', now_width, 268, prop_name_font, '#252525')
    img.text(chara.birthday if chara.birthday != '0/0' else '-', (now_width, now_width + bir_length), 308, prop_value_font, '#252525', 'center')
    now_width += bir_length + clearance
    img.text('数据以90级为准', 1485, 195, prop_name_font, '#252525', 'right')
    # ---------------基础数据---------------

    # ---------------培养材料---------------
    materials = chara.get_material_group()
    i = 0
    book_pass = False
    for material in materials:
        name = material['material'].name
        if name == '智识之冕' or (chara.name == '旅行者' and name == '历战的箭簇'):
            continue
        elif len(name) == 7 and name.startswith('「') and name[3] == '」':
            if book_pass:
                continue
            if len(next_name := materials[materials.index(material) + 1]['material'].name) == 7 and next_name.startswith('「') and next_name[3] == '」':
                book_pass = True
                name = '多种天赋书'
            else:
                name = f'{name[:4]}书'
        elif chara.name == '旅行者' and chara.element == '岩':
            if i == 5:
                name = '多周本材料'
            elif i > 5:
                break
        elif len(name) > 5:
            name = name[:5]
        img.paste(CHARACTER_MAP_RESOURCES / '圆框.png', (641 + i * 143, 472))
        icon_img = download_from_ambr(MATERIALS / f'{material["material"].icon}.png')
        icon_img = icon_img.resize((100, 100))
        img.paste(icon_img, (651 + i * 143, 482))
        img.draw_rounded_rectangle((642 + i * 143, 567, 765 + i * 143, 597), 5, '#ff6f30')
        img.text(name, (642 + i * 143, 765 + i * 143), (567, 597), talent_data_font, 'white', 'center')
        i += 1
    # ---------------培养材料---------------

    # ---------------天赋和命座数据---------------
    img.text('数据以第九级对应天赋为准', 1485, 645, prop_name_font, '#252525', 'right')
    talent_imgs = [draw_talent(v, int(k), chara.name) for k, v in chara.talent.items() if v.icon]
    constellation_imgs = [draw_constellation(v) for v in chara.constellation.values()]
    this_height_now = 699 + 21
    if (h1 := sum(i.height for i in talent_imgs) + (len(talent_imgs) - 1) * 50) >= (h2 := sum(i.height for i in constellation_imgs) + (len(constellation_imgs) - 1) * 120):
        this_height = h1 + 42
        img.stretch((719, 2217), this_height - 40, 'height')
        clearance = min((this_height - h2) // (len(constellation_imgs) - 1), 120)
        for talent_img in talent_imgs:
            img.paste(talent_img, (620, this_height_now))
            this_height_now += talent_img.height + 50
        this_height_now = 699 + 21
        for constellation_img in constellation_imgs:
            img.paste(constellation_img, (35, this_height_now))
            this_height_now += constellation_img.height + clearance
        img.text('制作：西北一枝花&惜月', 60, img.height - 90, prop_name_font, '#252525')
    else:
        this_height = h2 + 42
        img.stretch((719, 2217), this_height - 40, 'height')
        clearance = min((this_height - h1) // (len(talent_imgs) - 1), 50)
        for constellation_img in constellation_imgs:
            img.paste(constellation_img, (35, this_height_now))
            this_height_now += constellation_img.height + 80
        this_height_now = 699 + 21
        for talent_img in talent_imgs:
            img.paste(talent_img, (620, this_height_now))
            this_height_now += talent_img.height + clearance
        img.text('制作：西北一枝花&惜月', 1477, img.height - 90, prop_name_font, '#252525', 'right')
    # ---------------天赋和命座数据---------------
    bg_img = PMImage(CHARACTER_MAP_RESOURCES / '背景色.png')
    bg_img.stretch((50, bg_img.height - 50), img.height - 100, 'height')
    border_img = PMImage(CHARACTER_MAP_RESOURCES / '边框.png')
    border_img.stretch((50, border_img.height - 50), img.height - 100, 'height')
    bg_img.paste(border_img, (0, 0))
    bg_img.covered(ICON / '方块纹理.png')
    bg_img.paste(img, (0, 0))
    bg_img.save(CHARACTER_MAP_RESULT_RAW / f'{chara.id}.png')
    bg_img.convert('RGB')
    if chara.name == '旅行者':
        save_name = f'{chara.element}荧' if chara.icon.endswith('PlayerGirl') else f'{chara.element}空'
    else:
        save_name = chara.name
    bg_img.save(CHARACTER_MAP_RESULT / f'{save_name}.jpg', mode='JPEG', quality=50)
    print(f'>>>>>>角色[{chara.name}]图鉴 制作完成')
    # bg_img.show()


if __name__ == '__main__':
    draw_character_map(Character.parse_file(Path(__file__).parent / 'data' / 'raw' / 'avatar' / '10000052.json'))
