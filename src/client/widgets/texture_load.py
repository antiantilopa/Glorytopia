from pathlib import Path
from engine_antiantilopa import *
import json
import os



ASSET_PATH = Path() / "client" / "assets"
# in src

SpriteComponent.set_default("default")

def load_textures(texture_packs: list[str] = ["default"]):

    for texture_pack in texture_packs:
        if texture_pack not in os.listdir(ASSET_PATH):
            continue
    
        if not os.path.isfile(ASSET_PATH / texture_pack / "config.json"):
            continue
        
        with open(ASSET_PATH / texture_pack / "config.json", "r") as f:
            textures_json = (json.load(f))

        load_from_json(textures_json["textures"], prefix="", texture_pack=texture_pack)


def load_from_json(json_data: dict[str, str|dict], prefix: str = "", texture_pack: str = "default"):
    for key, item in json_data.items():
        if isinstance(item, dict):
            load_from_json(item, prefix + key + ":", texture_pack=texture_pack)
            continue
        try:
            name = prefix + key
            file_name = item
            if SpriteComponent.is_downloaded(nickname=name):
                continue
            SpriteComponent(path=(ASSET_PATH / texture_pack / "textures" / file_name).absolute().as_posix(), nickname=name)
        except Exception as e:
            print(f"error occured while reading texture: {file_name} form texture pack: {texture_pack}")
            print(e)