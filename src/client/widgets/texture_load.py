from engine_antiantilopa import *
from shared import *
import os, json

def load_textures(texture_packs: list[str] = ["default"]):
    path = str.join("/", [*(__file__).split("\\")[:-2], "assets"]) + "/"
    for texture_pack in texture_packs:
        if texture_pack not in os.listdir(path):
            continue
    
        if not os.path.isfile(path + texture_pack + "/config.json"):
            continue

        with open(path + texture_pack + "/config.json", "r") as f:
            textures_json = (json.load(f))


        for name, types in {"tiles": TileType.ttypes, "resources": ResourceType.rtypes, "techs": TechNode.techs, "buildings": BuildingType.btypes, "units": UnitType.utypes}.items():
            for type in types:
                if f":{type.name}" in SpriteComponent.downloaded:
                    continue
                if type.name in textures_json["textures"][name]:
                    texture_path = path + texture_pack + "/textures"
                    try:
                        SpriteComponent(texture_path + "/" + textures_json["textures"][name][type.name], Vector2d(100, 100), nickname=type.name)
                    except FileNotFoundError:
                        pass
        if ":city" in SpriteComponent.downloaded:
            continue
        if "city" in textures_json["textures"]:
            texture_path = path + texture_pack + "/textures"
            try:
                SpriteComponent(texture_path + "/" + textures_json["textures"]["city"], Vector2d(100, 100), nickname="city")
            except FileNotFoundError:
                pass
    for name, types in {"tiles": TileType.ttypes, "resources": ResourceType.rtypes, "techs": TechNode.techs, "buildings": BuildingType.btypes, "units": UnitType.utypes}.items():
        for type in types:
            if f":{type.name}" not in SpriteComponent.downloaded:
                print(f"Texture for {name[:-1]} {type.name} not found in any texture pack!")
                SpriteComponent(path + "default" + "/textures" + "/default.png", Vector2d(100, 100), nickname=type.name)
    if ":city" not in SpriteComponent.downloaded:
        print("Texture for city not found in any texture pack!")
        SpriteComponent(path + "default" + "/textures" + "/default.png", Vector2d(100, 100), nickname="city")