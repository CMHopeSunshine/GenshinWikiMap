from AmbrApi.models import Character
from AmbrApi.handler import update_material_need, get_update_characters_map, update_constant, update_artifact_info
from draw_character_map import draw_character_map
from utils import load_json
from path import AVATAR_RAW


def main():
    update_constant()
    need_draw = get_update_characters_map()
    update_material_need()
    for avatar_id in need_draw:
        avatar_info = load_json(AVATAR_RAW / f'{avatar_id}.json')
        character = Character.parse_obj(avatar_info)
        draw_character_map(character)
    update_artifact_info()


if __name__ == '__main__':
    main()