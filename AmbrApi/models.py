import re
from typing import Optional, Union, TypedDict
from pydantic import BaseModel, validator
from collections import defaultdict

from path import DATA, RAW
from utils import load_json


ELEMENT_MAP = {
    'Wind':     '风',
    'Ice':      '冰',
    'Grass':    '草',
    'Water':    '水',
    'Electric': '雷',
    'Rock':     '岩',
    'Fire':     '火',
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


CharacterMaterialItem = TypedDict('CharacterMaterialItem', {
    'material': MaterialItem,
    'count':    Union[int, list[int]],
})


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
    propType: str
    initValue: float
    type: str


class Promote(BaseModel):
    promoteLevel: int
    unlockMaxLevel: int
    costItems: Optional[dict[str, int]]
    addProps: Optional[dict[str, float]]
    requiredPlayerLevel: Optional[int]
    coinCost: Optional[int]


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
    specialFood: Optional[SpecialFood]


class TalentPromote(BaseModel):
    level: int
    costItems: Optional[dict[str, int]]
    coinCost: Optional[int]
    description: list[str]
    params: list[float]

    @validator('description', pre=True)
    def format_description(cls, value: list[str]):
        return [v for v in value if v]

    # @validator('params', pre=True)
    # def format_params(cls, value: list[float]):
    #     return value[:13]


class Talent(BaseModel):
    type: int
    name: str
    description: str
    icon: str
    promote: Optional[dict[str, TalentPromote]]
    cooldown: Optional[int]
    cost: Optional[int]

    def get_promote_list(self) -> Optional[dict[str, list[str]]]:
        if self.promote is None:
            return None
        new_dict = {item.split('|')[0]: [] for item in self.promote['1'].description}
        for promote in self.promote.values():
            for desc in promote.description:
                desc_name, param_str = desc.split('|')
                for param in re.findall(r'{param\d+:(?:F1P|F1|P|I|F2P)}', param_str):
                    split = param.strip('{').strip('}').split(':')
                    num, fm = int(re.search(r'\d+', split[0]).group()), split[1]
                    if self.name == '蒲公英之风' and num >= 8:  # 琴的大招技能参数有问题
                        num -= 1
                    p = promote.params[num - 1]
                    param_str = param_str.replace(param,
                                                  f'{str(round(p * 100, 1))}%' if fm in ['F1P', 'P', 'F2P'] else str(
                                                      int(p)))
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
    other: Optional[Other]
    ascension: dict[str, int]
    talent: dict[str, Talent]
    constellation: dict[str, Constellation]
    beta: bool = False

    @validator('element', pre=True)
    def format_element(cls, value: str):
        return ELEMENT_MAP[value]

    @validator('weaponType', pre=True)
    def format_weaponType(cls, value: str):
        return load_json(RAW / 'prop_map.json')[value]

    @validator('birthday', pre=True)
    def format_birthday(cls, value: list[int]):
        return f'{value[0]}/{value[1]}'

    @property
    def health(self) -> int:
        """90级基础生命值"""
        return int(round(
            self.upgrade.prop[0].initValue * load_json(RAW / 'avatar_curve.json')['90']['curveInfos'][
                self.upgrade.prop[0].type] +
            self.upgrade.promote[-1].addProps['FIGHT_PROP_BASE_HP'], 0))

    @property
    def attack(self) -> int:
        """90级基础攻击力"""
        return int(round(
            self.upgrade.prop[1].initValue * load_json(RAW / 'avatar_curve.json')['90']['curveInfos'][
                self.upgrade.prop[1].type] +
            self.upgrade.promote[-1].addProps['FIGHT_PROP_BASE_ATTACK'], 0))

    @property
    def defense(self) -> int:
        """90级基础防御力"""
        return int(round(
            self.upgrade.prop[2].initValue * load_json(RAW / 'avatar_curve.json')['90']['curveInfos'][
                self.upgrade.prop[2].type] +
            self.upgrade.promote[-1].addProps['FIGHT_PROP_BASE_DEFENSE'], 0))

    @property
    def extra_prop_name(self) -> str:
        """突破属性名称"""
        return load_json(RAW / 'prop_map.json')[list(self.upgrade.promote[-1].addProps.keys())[-1]]

    @property
    def extra_prop_value(self) -> Union[float, int]:
        """突破属性值"""
        return list(self.upgrade.promote[-1].addProps.values())[-1]

    @property
    def title_name(self) -> str:
        """标题+名字"""
        if self.name == '旅行者':
            return '「旅行者·荧」' if self.icon.endswith('PlayerGirl') else '「旅行者·空」'
        return f'「{self.fetter.title}·{self.name}」'

    def get_material_list(self) -> list[CharacterMaterialItem]:
        """素材列表"""
        material_list: list[CharacterMaterialItem] = []
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
            if mat := load_json(RAW / 'materials.json')['items'].get(item):
                material_list.append(CharacterMaterialItem(material=MaterialItem.parse_obj(mat), count=num))
        material_list.sort(key=lambda x: x['material'].id)
        return material_list

    def get_material_ids(self) -> list[int]:
        """素材id列表"""
        return [item['material'].id for item in self.get_material_list()]

    def get_material_group(self):
        """素材分组"""
        material_list = self.get_material_list()
        material_group: list[CharacterMaterialItem] = []
        temp_group = defaultdict(list)
        for material in material_list:
            if group := list(filter(lambda x: material['material'].name in x[1],
                                    load_json(DATA / '材料组.json').items())):
                temp_group[group[0][0]].append(material['count'])
        material_group.extend(
            CharacterMaterialItem(
                material=MaterialItem.parse_obj(load_json(RAW / 'materials.json')['items'][material_id]), count=num) for
            material_id, num in temp_group.items())

        return material_group
# -----------------角色相关-----------------
