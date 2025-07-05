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
        for key in ("city", "city_walls", "city_forge"):
            if SpriteComponent.is_downloaded(key):
                continue
            if key in textures_json["textures"]["city"]:
                texture_path = path + texture_pack + "/textures"
                try:
                    SpriteComponent(texture_path + "/" + textures_json["textures"]["city"][key], Vector2d(100, 100), nickname=key)
                except FileNotFoundError:
                    pass
    for name, types in {"tiles": TileType.ttypes, "resources": ResourceType.rtypes, "techs": TechNode.techs, "buildings": BuildingType.btypes, "units": UnitType.utypes}.items():
        for type in types:
            if f":{type.name}" not in SpriteComponent.downloaded:
                print(f"Texture for {name[:-1]} {type.name} not found in any texture pack!")
                try:
                    if name == "units":
                        SpriteComponent(path + "default" + "/textures" + "/default_unit.png", Vector2d(100, 100), nickname=type.name)
                    elif name == "techs":
                        SpriteComponent(path + "default" + "/textures" + "/default_tech.png", Vector2d(100, 100), nickname=type.name)
                    elif name == "tiles":
                        SpriteComponent(path + "default" + "/textures" + "/default_tile.png", Vector2d(100, 100), nickname=type.name)
                    elif name == "buildings":
                        SpriteComponent(path + "default" + "/textures" + "/default_building.png", Vector2d(100, 100), nickname=type.name)
                    elif name == "resources":
                        SpriteComponent(path + "default" + "/textures" + "/default_resource.png", Vector2d(100, 100), nickname=type.name)
                except FileNotFoundError:
                    SpriteComponent(path + "default" + "/textures" + "/default.png", Vector2d(100, 100), nickname=type.name)
                
    if ":city" not in SpriteComponent.downloaded:
        print("Texture for city not found in any texture pack!")
        SpriteComponent(path + "default" + "/textures" + "/default.png", Vector2d(100, 100), nickname="city")