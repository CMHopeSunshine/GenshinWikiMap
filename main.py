from AmbrApi.models import Character
from update import update_material_info, update_characters, update_monster_info, update_constant, update_artifact_info, update_type_info, update_weapon_info
from draw_character_map import draw_character_map
from utils import load_json
from path import AVATAR_RAW


def main():
    # update_constant()
    # update_weapon_info()
    # need_draw = get_update_characters_map()
    # update_material_info()
    # for avatar_id in need_draw:
    #     avatar_info = load_json(AVATAR_RAW / f'{avatar_id}.json')
    #     character = Character.parse_obj(avatar_info)
    #     draw_character_map(character)
    # update_artifact_info()
    # update_type_info()
    # update_material_info()
    update_monster_info()

if __name__ == '__main__':
    main()