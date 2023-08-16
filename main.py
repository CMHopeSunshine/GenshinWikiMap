from update import (
    update_material,
    update_character,
    update_monster,
    update_constant,
    update_artifact,
    update_weapon)


def main():
    update_constant()
    update_character()
    update_weapon()
    update_monster()
    update_artifact()
    update_material()


if __name__ == '__main__':
    main()
