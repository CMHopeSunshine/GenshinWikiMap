import re
from collections import defaultdict
from typing import Optional, Union

from pydantic import BaseModel, validator

from path import DATA, RAW
from utils import load_json

from .api import WEAPON_STORY_API
from .data_source import ambr_requests

ELEMENT_MAP = {
    "Wind": "风",
    "Ice": "冰",
    "Grass": "草",
    "Water": "水",
    "Electric": "雷",
    "Rock": "岩",
    "Fire": "火",
}


# -----------------材料相关-----------------
class MaterialItem(BaseModel):
    id: int
    name: str
    type: str
    recipe: bool
    mapMark: bool
    icon: str
    rank: int
    route: str


class MaterialItemCount(BaseModel):
    material: MaterialItem
    count: Union[int, list[int]]


# -----------------材料相关-----------------

# -----------------角色相关-----------------


class CV(BaseModel):
    """配音"""

    EN: str
    CHS: str
    JP: str
    KR: str


class Fetter(BaseModel):
    title: str
    detail: str
    constellation: str
    native: str
    cv: CV


class Prop(BaseModel):
    propType: Optional[str] = None
    initValue: float
    type: str


class Promote(BaseModel):
    promoteLevel: int
    unlockMaxLevel: int
    costItems: Optional[dict[str, int]] = None
    addProps: Optional[dict[str, float]] = None
    requiredPlayerLevel: Optional[int] = None
    coinCost: Optional[int] = None


class Upgrade(BaseModel):
    prop: list[Prop]
    promote: list[Promote]


class NameCard(BaseModel):
    id: str  # 凝光的名片id有问题
    name: str
    description: str
    icon: str


class SpecialFood(BaseModel):
    id: int
    name: str
    rank: int
    effectIcon: str
    icon: str


class Other(BaseModel):
    nameCard: NameCard
    specialFood: Optional[SpecialFood] = None


class TalentPromote(BaseModel):
    level: int
    costItems: Optional[dict[str, int]] = None
    coinCost: Optional[int] = None
    description: list[str]
    params: list[float]

    @validator("description", pre=True)
    def format_description(cls, value: list[str]):
        return [v for v in value if v]


class Talent(BaseModel):
    type: int
    name: str
    description: str
    icon: str
    promote: Optional[dict[str, TalentPromote]] = None
    cooldown: Optional[int] = None
    cost: Optional[int] = None

    def get_promote_list(self) -> Optional[dict[str, list[str]]]:
        if self.promote is None:
            return None
        new_dict = {item.split("|")[0]: [] for item in self.promote["1"].description}
        for promote in self.promote.values():
            for desc in promote.description:
                desc_name, param_str = desc.split("|")
                desc_name = "点按拍照伤害" if desc_name == "点按相机伤害" else desc_name
                for param in re.findall(r"{param\d+:(?:F1P|F1|P|I|F2P|F2)}", param_str):
                    split = param.strip("{").strip("}").split(":")
                    num, fm = int(re.search(r"\d+", split[0]).group()), split[1]  # type: ignore
                    if self.name == "蒲公英之风" and num >= 8:  # 琴的大招技能参数有问题
                        num -= 1
                    p = promote.params[num - 1]
                    param_str = param_str.replace(
                        param,
                        (
                            f"{str(round(p * 100, 1))}%"
                            if fm in ["F1P", "P", "F2P", "F2"]
                            else str(int(p))
                        ),
                    )
                new_dict[desc_name].append(param_str)

        return new_dict


class Constellation(BaseModel):
    name: str
    description: str
    icon: str


class Character(BaseModel):
    id: str
    rank: int
    name: str
    element: str
    weaponType: str
    icon: str
    birthday: str
    release: int
    route: str
    fetter: Fetter
    upgrade: Upgrade
    other: Optional[Other] = None
    ascension: dict[str, int]
    talent: dict[str, Talent]
    constellation: dict[str, Constellation]
    beta: bool = False

    @validator("element", pre=True)
    def format_element(cls, value: str):
        return ELEMENT_MAP[value]

    @validator("weaponType", pre=True)
    def format_weaponType(cls, value: str):
        return load_json(DATA / "属性Map.json")[value]

    @validator("birthday", pre=True)
    def format_birthday(cls, value: list[int]):
        return f"{value[0]}/{value[1]}"

    @property
    def health(self) -> int:
        """90级基础生命值"""
        assert self.upgrade.promote[-1].addProps
        return int(
            round(
                self.upgrade.prop[0].initValue
                * load_json(RAW / "avatar_curve.json")["90"]["curveInfos"][
                    self.upgrade.prop[0].type
                ]
                + self.upgrade.promote[-1].addProps["FIGHT_PROP_BASE_HP"],
                0,
            )
        )

    @property
    def attack(self) -> int:
        """90级基础攻击力"""
        assert self.upgrade.promote[-1].addProps
        return int(
            round(
                self.upgrade.prop[1].initValue
                * load_json(RAW / "avatar_curve.json")["90"]["curveInfos"][
                    self.upgrade.prop[1].type
                ]
                + self.upgrade.promote[-1].addProps["FIGHT_PROP_BASE_ATTACK"],
                0,
            )
        )

    @property
    def defense(self) -> int:
        """90级基础防御力"""
        assert self.upgrade.promote[-1].addProps
        return int(
            round(
                self.upgrade.prop[2].initValue
                * load_json(RAW / "avatar_curve.json")["90"]["curveInfos"][
                    self.upgrade.prop[2].type
                ]
                + self.upgrade.promote[-1].addProps["FIGHT_PROP_BASE_DEFENSE"],
                0,
            )
        )

    @property
    def extra_prop_name(self) -> str:
        """突破属性名称"""
        assert self.upgrade.promote[-1].addProps
        return load_json(DATA / "属性Map.json")[
            list(self.upgrade.promote[-1].addProps.keys())[-1]
        ]

    @property
    def extra_prop_value(self) -> Union[float, int]:
        """突破属性值"""
        assert self.upgrade.promote[-1].addProps
        return list(self.upgrade.promote[-1].addProps.values())[-1]

    @property
    def title_name(self) -> str:
        """标题+名字"""
        if self.name == "旅行者":
            return (
                "「旅行者·荧」" if self.icon.endswith("PlayerGirl") else "「旅行者·空」"
            )
        return f"「{self.fetter.title}·{self.name}」"

    def get_material_list(self) -> list[MaterialItemCount]:
        """素材列表"""
        material_list: list[MaterialItemCount] = []
        material_ids = defaultdict(int)
        for promote in self.upgrade.promote:
            if promote.costItems is None:
                continue
            for item, num in promote.costItems.items():
                material_ids[item] += num
        for talent in self.talent.values():
            if talent.promote is None:
                continue
            for promote in talent.promote.values():
                if promote.costItems is None:
                    continue
                for item, num in promote.costItems.items():
                    material_ids[item] += num
        for item, num in material_ids.items():
            if mat := load_json(RAW / "materials.json")["items"].get(item):
                material_list.append(
                    MaterialItemCount(material=MaterialItem.parse_obj(mat), count=num)
                )
        material_list.sort(key=lambda x: x.material.id)
        return material_list

    def get_material_ids(self) -> list[int]:
        """素材id列表"""
        return [item.material.id for item in self.get_material_list()]

    def get_material_group(self):
        """素材分组"""
        material_list = self.get_material_list()
        material_group: list[MaterialItemCount] = []
        temp_group = defaultdict(list)
        for material in material_list:
            if group := list(
                filter(
                    lambda x: material.material.name in x[1],
                    load_json(DATA / "材料组.json").items(),
                )
            ):
                temp_group[group[0][0]].append(material.count)
        material_group.extend(
            MaterialItemCount(
                material=MaterialItem.parse_obj(
                    load_json(RAW / "materials.json")["items"][material_id]
                ),
                count=num,
            )
            for material_id, num in temp_group.items()
        )

        return material_group

    # def save_to_dict(self) -> dict:
    #     return {
    #         'id': self.id,
    #         '名称': self.name,
    #         '元素': self.element,
    #         '武器': self.weaponType,
    #         '星级': self.rank,
    #         '生日': self.birthday,
    #         '图标': {
    #             '头像': self.icon,
    #             '侧脸': self.icon.replace('AvatarIcon', 'AvatarIcon_Side'),
    #             '卡片': self.icon + '_Card',
    #             '立绘': self.icon.replace('AvatarIcon', 'Gacha_AvatarImg'),
    #             '立绘竖条': self.icon.replace('AvatarIcon', 'Gacha_AvatarIcon')
    #         },
    #         '名片': {
    #             'id': self.other.nameCard.id,
    #             '名称': self.other.nameCard.name,
    #             '描述': self.other.nameCard.description,
    #             '图标': self.other.nameCard.icon
    #         },
    #         '特色食物': {
    #             'id': self.other.specialFood.id,
    #             '名称': self.other.specialFood.name,
    #             '星级': self.other.specialFood.rank,
    #             '图标': self.other.specialFood.icon
    #         } if self.other.specialFood else None,
    #         '地区': load_json(DATA / '角色地区.json').get(self.name, '未知'),
    #     }


# -----------------角色相关-----------------


# -----------------武器相关-----------------
class WeaponAffix(BaseModel):
    name: str
    upgrade: dict[str, str]


class WeaponUpgrade(BaseModel):
    awakenCost: list[int]
    prop: list[Prop]
    promote: list[Promote]


class Weapon(BaseModel):
    id: str
    rank: int
    name: str
    type: str
    description: str
    icon: str
    storyId: int
    affix: Optional[dict[str, WeaponAffix]] = None
    route: str
    upgrade: WeaponUpgrade
    ascension: dict[str, int]
    beta: bool = False

    @property
    def story(self) -> Optional[str]:
        if (text := ambr_requests(WEAPON_STORY_API.format(self.id))) and isinstance(
            text, str
        ):
            return text.replace("\r\n", "")
        else:
            return None

    @property
    def skill(self) -> Optional[dict]:
        if self.affix:
            affix = list(self.affix.values())[0]
            return {
                "id": list(self.affix.keys())[0],
                "名称": affix.name,
                "效果": list(affix.upgrade.values()),
            }
        else:
            return None

    @property
    def attack(self) -> int:
        """90级基础攻击力"""
        assert self.upgrade.promote[-1].addProps
        return int(
            round(
                self.upgrade.prop[0].initValue
                * load_json(RAW / "weapon_curve.json")["90"]["curveInfos"][
                    self.upgrade.prop[0].type
                ]
                + self.upgrade.promote[-1].addProps["FIGHT_PROP_BASE_ATTACK"],
                0,
            )
        )

    @property
    def extra_prop_name(self) -> str:
        """突破属性名称"""
        if self.upgrade.prop[1].propType:
            return load_json(DATA / "属性Map.json")[self.upgrade.prop[1].propType]
        else:
            return "无"

    @property
    def extra_prop_value(self) -> float:
        """突破属性值"""
        if self.upgrade.prop[1].propType:
            return round(
                self.upgrade.prop[1].initValue
                * load_json(RAW / "weapon_curve.json")["90"]["curveInfos"][
                    self.upgrade.prop[1].type
                ],
                3,
            )
        else:
            return 0

    def get_material_list(self) -> list[MaterialItemCount]:
        """素材列表"""
        material_data = load_json(RAW / "materials.json")["items"]
        material_list: list[MaterialItemCount] = []
        material_ids = defaultdict(int)
        for promote in self.upgrade.promote:
            if promote.costItems is None:
                continue
            for item, num in promote.costItems.items():
                material_ids[item] += num
        for item, num in material_ids.items():
            if mat := material_data.get(item):
                material_list.append(
                    MaterialItemCount(material=MaterialItem.parse_obj(mat), count=num)
                )
        material_list.sort(key=lambda x: x.material.id)
        return material_list

    def get_material_group(
        self, material_list: Optional[list[MaterialItemCount]] = None
    ):
        """素材分组"""
        if material_list is None:
            material_list = self.get_material_list()
        material_group: list[MaterialItemCount] = []
        temp_group = defaultdict(list)
        for material in material_list:
            if group := list(
                filter(
                    lambda x: material.material.name in x[1],
                    load_json(DATA / "材料组.json").items(),
                )
            ):
                temp_group[group[0][0]].append(material.count)
        material_group.extend(
            MaterialItemCount(
                material=MaterialItem.parse_obj(
                    load_json(RAW / "materials.json")["items"][material_id]
                ),
                count=num,
            )
            for material_id, num in temp_group.items()
        )

        return material_group

    def save_data(self) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "rank": self.rank,
            "type": self.type,
            "icon": {
                "icon": self.icon,
                "awaken": self.icon + "_Awaken",
                "gacha": self.icon.replace("UI_EquipIcon", "UI_Gacha_EquipIcon"),
            },
            "property": [
                {
                    "base": self.upgrade.prop[0].dict(),
                    "promote": [
                        p.addProps["FIGHT_PROP_BASE_ATTACK"] if p.addProps else None
                        for p in self.upgrade.promote[1:]
                    ],
                }
            ],
        }
        if len(self.upgrade.prop) > 1 and self.upgrade.prop[1].propType:
            data["property"].append({"base": self.upgrade.prop[1].dict()})
        return data

    def save_detail(self) -> dict:
        return {
            "id": self.id,
            "名称": self.name,
            "星级": self.rank,
            "类型": self.type,
            "图标": self.icon,
            "描述": self.description,
            "基础攻击力": self.attack,
            "副属性": {"名称": self.extra_prop_name, "数值": self.extra_prop_value},
            "技能": self.skill,
            "buff": {"常驻": [], "战斗时": [], "队伍": []},
            "材料": {
                material.material.name: material.count
                for material in self.get_material_list()
            },
            "材料分组": {
                material.material.name: material.count
                for material in self.get_material_group()
            },
            "故事": self.story,
        }


# -----------------武器相关-----------------


# -----------------原魔相关-----------------
MONSTER_TYPE_MAP = {
    "ELEMENTAL": "元素生命",
    "HILICHURL": "丘丘部族",
    "ABYSS": "深渊",
    "FATUI": "愚人众",
    "AUTOMATRON": "自律机关",
    "HUMAN": "其他人类势力",
    "BEAST": "异种魔兽",
    "BOSS": "值得铭记的强敌",
    "AVIARY": "禽鸟",
    "ANIMAL": "走兽",
    "FISH": "游鱼",
    "CRITTER": "其他",
}


class MonsterResistance(BaseModel):
    fireSubHurt: float = 0.1
    grassSubHurt: float = 0.1
    waterSubHurt: float = 0.1
    elecSubHurt: float = 0.1
    windSubHurt: float = 0.1
    iceSubHurt: float = 0.1
    rockSubHurt: float = 0.1
    physicalSubHurt: float = 0.1


class MonsterAffix(BaseModel):
    name: str
    description: str
    abilityName: list[str]
    isCommon: Optional[bool] = None


class MonsterReward(BaseModel):
    rank: int
    icon: str
    count: Optional[str] = None


class MonsterEntry(BaseModel):
    id: int
    type: str
    affix: Optional[list[MonsterAffix]] = None
    hpDrops: Optional[list[dict]] = None
    prop: list[Prop]
    resistance: Optional[MonsterResistance] = None
    reward: Optional[dict[str, MonsterReward]] = None

    def get_health_num(self, level: str) -> int:
        return int(
            self.prop[0].initValue
            * load_json(RAW / "monster_curve.json")[level]["curveInfos"][
                self.prop[0].type
            ]
        )

    def get_attack_num(self, level: str) -> int:
        return int(
            self.prop[1].initValue
            * load_json(RAW / "monster_curve.json")[level]["curveInfos"][
                self.prop[1].type
            ]
        )

    def get_defense_num(self, level: str) -> int:
        return int(
            self.prop[2].initValue
            * load_json(RAW / "monster_curve.json")[level]["curveInfos"][
                self.prop[2].type
            ]
        )

    def get_material_group(self) -> list[dict]:
        assert self.reward
        material_data = load_json(RAW / "materials.json")["items"]
        material_group_data = load_json(DATA / "材料组.json")
        return [
            material_data[material]
            for material in self.reward
            if material in material_group_data
        ]


class Monster(BaseModel):
    id: int
    name: str
    type: str
    icon: str
    route: str
    title: Optional[str] = None
    specialName: Optional[str] = None
    description: str
    entries: dict[str, MonsterEntry]
    tips: Optional[dict] = None


# -----------------原魔相关-----------------
