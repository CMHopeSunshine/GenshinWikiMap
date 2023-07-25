import math
from image_utils import PMImage
from utils import save_json
from path import RAW, DATA, RESOURCES
from AmbrApi import ambr_requests
from AmbrApi.api import (
    DAILY_URL,
    UPGRADE_URL,
    WEAPON_LIST_API,
    AVATAR_LIST_API,
    MATERIAL_LIST_API,
)

week_cn = {
    "monday": "周一",
    "tuesday": "周二",
    "wednesday": "周三",
    "thursday": "周四",
    "friday": "周五",
    "saturday": "周六",
}

DMPATH = RESOURCES / 'daily_material'


def get_daily_material():
    daily_info = {"天赋": {}, "武器": {}}
    if daily_data := ambr_requests(DAILY_URL):
        save_json(daily_data, RAW / "daily.json")
    else:
        return
    if material_data := ambr_requests(MATERIAL_LIST_API):
        save_json(material_data, RAW / "materials.json")
    else:
        return
    if upgrade_data := ambr_requests(UPGRADE_URL):
        save_json(upgrade_data, RAW / "upgrade.json")
    else:
        return
    if avatar_data := ambr_requests(AVATAR_LIST_API):
        save_json(avatar_data["items"], RAW / "avatar_list.json")
    else:
        return
    if weapon_data := ambr_requests(WEAPON_LIST_API):
        save_json(weapon_data["items"], RAW / "weapon_list.json")
    else:
        return
    detail_data = {"avatar": avatar_data["items"], "weapon": weapon_data["items"]}
    for week in daily_data:
        if week == "sunday":
            continue
        daily_info["天赋"][week_cn[week]], daily_info["武器"][week_cn[week]] = {}, {}
        domain_data = daily_data[week]
        domain_data_sort = sorted(domain_data, key=lambda x: domain_data[x]["city"])
        for domain_key in domain_data_sort:
            item_type = (
                "avatar"
                if domain_data[domain_key]["name"].startswith("精通秘境")
                else "weapon"
            )
            material = material_data["items"][
                str(domain_data[domain_key]["reward"][-1])
            ]
            used = []
            used = [
                (upgrade_data[item_type][id], detail_data[item_type][id]["name"])
                for id in upgrade_data[item_type]
                if str(material["id"]) in upgrade_data[item_type][id]["items"]
                and "Player" not in upgrade_data[item_type][id]["icon"]
                and not upgrade_data[item_type][id].get("beta", False)
            ]

            daily_info["天赋" if item_type == "avatar" else "武器"][week_cn[week]][
                f'{material["name"]}-{material["icon"]}'
            ] = [f'{u["rank"]}{u["icon"]}-{name}' for u, name in used]
    return daily_info
    # save_json(daily_info, DATA  / "daily_materials.json")


async def draw_material(daily_info: dict, week: str = '周一'):
    if week in {'周一', '周四'}:
        week_str = '周一/周四'
    elif week in {'周二', '周五'}:
        week_str = '周二/周五'
    else:
        week_str = '周三/周六'
    avatar = daily_info['天赋'][week]
    weapon = daily_info['武器'][week]
    total_height = 70 * len(weapon) + sum(math.ceil(len(items) / 5) * 160 for items in weapon.values()) + 165
    img = PMImage(DMPATH / 'bg.png')
    await img.stretch((50, img.width - 50), 1520, 'width')
    await img.stretch((50, img.height - 50), total_height - 100, 'height')
    frame = await load_image(RESOURCE_BASE_PATH / 'general' / 'frame.png')
    await img.paste(frame, (190, 62))
    await img.paste(frame, (1000, 62))
    await img.text(f'{week_str}角色天赋材料', 223, 69, fm.get('SourceHanSerifCN-Bold.otf', 35), 'black')
    await img.text(f'{week_str}武器突破材料', 1033, 69, fm.get('SourceHanSerifCN-Bold.otf', 35), 'black')
    star_bg = {
        '3': await load_image(RESOURCE_BASE_PATH / 'icon' / 'star3.png', size=(110, 110)),
        '4': await load_image(RESOURCE_BASE_PATH / 'icon' / 'star4.png', size=(110, 110)),
        '5': await load_image(RESOURCE_BASE_PATH / 'icon' / 'star5.png', size=(110, 110))
    }
    now_height = 165
    for name, items in avatar.items():
        name, icon = name.split('-')
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'star5.png', size=(60, 60)), (90, now_height))
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'material' / f'{icon}.png', size=(60, 60)),
                        (90, now_height))
        await img.text(name, 165, now_height + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'black')
        now_height += 70
        items.sort(key=lambda x: int(x[0]), reverse=True)
        for i in range(len(items)):
            star = items[i][0]
            icon = items[i][1:].split('-')[0]
            name_ = items[i][1:].split('-')[1]
            await img.paste(star_bg[star], (90 + 128 * (i % 5), now_height + 145 * int(i / 5)))
            await img.paste(await load_image(RESOURCE_BASE_PATH / 'avatar' / f'{icon}.png', size=(110, 110)),
                            (90 + 128 * (i % 5), now_height + 145 * int(i / 5)))
            await img.text(name_, (90 + 128 * (i % 5), 90 + 128 * (i % 5) + 110), now_height + 145 * int(i / 5) + 110,
                           fm.get('SourceHanSerifCN-Bold.otf', 20), 'green' if name_ in characters else 'black',
                           'center')
        now_height += math.ceil(len(items) / 5) * 145 + 70
    now_height = 165
    for name, items in weapon.items():
        name, icon = name.split('-')
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'star5.png', size=(60, 60)), (908, now_height))
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'material' / f'{icon}.png', size=(60, 60)),
                        (908, now_height))
        await img.text(name, 983, now_height + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'black')
        now_height += 70
        items.sort(key=lambda x: int(x[0]), reverse=True)
        for i in range(len(items)):
            star = items[i][0]
            icon = items[i][1:].split('-')[0]
            name_ = items[i][1:].split('-')[1]
            await img.paste(star_bg[star], (908 + 128 * (i % 5), now_height + 145 * int(i / 5)))
            await img.paste(await load_image(RESOURCE_BASE_PATH / 'weapon' / f'{icon}.png', size=(110, 110)),
                            (908 + 128 * (i % 5), now_height + 145 * int(i / 5)))
            await img.text(name_, (908 + 128 * (i % 5), 908 + 128 * (i % 5) + 110), now_height + 145 * int(i / 5) + 110,
                           fm.get('SourceHanSerifCN-Bold.otf', 20), 'green' if name_ in weapons else 'black', 'center')
        now_height += math.ceil(len(items) / 5) * 145 + 15
    await img.text('CREATED BY LITTLEPAIMON', (0, img.width), img.height - 83,
                   fm.get('bahnschrift_bold', 44, 'Bold'), '#3c3c3c', align='center')

    return MessageBuild.Image(img, mode='RGB', quality=80)