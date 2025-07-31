from engine_antiantilopa import *
from shared import *
from .sound import SoundComponent
import os

def load_sounds(texture_packs: list[str] = ["default"]):
    path = str.join("/", [*(__file__).split("\\")[:-2], "assets"]) + "/"
    for texture_pack in texture_packs:
        if texture_pack not in os.listdir(path):
            continue
    
        if not os.path.isfile(path + texture_pack + "/config.json"):
            continue
            
        for file in os.listdir(path + texture_pack + "/sounds/"):
            try:
                if SoundComponent.is_downloaded(nickname=file):
                    continue
                sound_path = path + texture_pack + "/sounds"
                if os.path.exists(sound_path + "/" + file + "/config.json"):
                    SoundComponent(path=sound_path + "/" + file, nickname=file)
            except KeyError:
                pass
            except Exception as e:
                print(f"error occured while reading {texture_pack}:{file}")
                print(e)