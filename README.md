# GenshinWikiMap
## 介绍
原神(Genshin Impact)游戏数据、图鉴制作以及资源库，数据和素材源自[miHoYo](https://www.mihoyo.com/)和[安柏计划](https://ambr.top/chs)。

目前主要用于原神Bot[小派蒙](https://github.com/CMHopeSunshine/LittlePaimon)。

## 图鉴
由[西北一枝花](https://github.com/Nwflower)设计模版，[惜月](https://github.com/CMHopeSunshine)编码制作。
- 角色图鉴
  - 路径：`results/character_map/`
  - 以角色**中文完整名**命名，含测试中角色
  - 天赋只有第九级的详细倍率
- 原魔图鉴(初版)
  - 路径：`results/monster_map/`
  - 以原魔**中文完整名**命名，含测试中原魔
  - 部分原魔缺失材料信息
  - 暂时只有常规形态抗性表

## 数据
本人整理过的原神相关数据文件，位于`data`文件夹
```
├── data
│   ├── artifact #圣遗物，以套装ID命名
│   │   ├── 10001.json
│   ├── avatar #角色，以角色ID命名
│   │   ├── 10000002.json
│   ├── weapon #武器，以武器ID命名
│   │   ├── 11101.json
│   ├── raw #ambr或其它的原始数据文件夹
│   │   ├── ......
│   ├── data.zip #数据文件zip
│   ├── data_list.json #数据文件列表及其hash
│   ├── **.json #其它中文名文件顾名思义
```

## 资源
原神相关图片、图标资源，位于`resources`文件夹
```
├── resources
│   ├── avatar #角色正面头像
│   │   ├── UI_AvatarIcon_Albedo.png
│   ├── avatar_side #角色侧面头像
│   │   ├── UI_AvatarIcon_Side_Albedo.png
│   ├── splash #角色抽卡立绘
│   │   ├── UI_Gacha_AvatarImg_Albedo.png
│   ├── talent #角色天赋和命座图标
│   │   ├── Skill_A_02.png
│   ├── weapon #武器头像
│   │   ├── UI_EquipIcon_Bow_Amos.png
│   ├── monster #原魔头像
│   │   ├── UI_MonsterIcon_Abyss_Ice.png
│   ├── material #材料图标
│   │   ├── UI_ItemIcon_100021.png
│   ├── ..... #其余为图鉴制作的相关资源
```

## 声明
- 本仓库所有数据和图鉴版权属于米哈游，侵删
- 如果你传播或要在其它项目使用本仓库制作的**游戏图鉴**，请先**联系我**取得授权，私人使用则无需
- 欢迎[爱发电](https://afdian.net/a/cherishmoon)赞助支持，感谢！

## 鸣谢
- [miHoYo](https://www.mihoyo.com/)
- [安柏计划](https://ambr.top/chs)
- [西北一枝花](https://github.com/Nwflower)
- PR贡献者们

## 其它相关项目
- [小派蒙](https://github.com/CMHopeSunshine/LittlePaimon)
- [小派蒙文档](https://docs.paimon.cherishmoon.fun)
- [小派蒙资源库](https://github.com/CMHopeSunshine/LittlePaimonRes)
- [Altas原神图鉴](https://github.com/Nwflower/genshin-atlas)
