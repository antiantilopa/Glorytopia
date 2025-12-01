from client.scenes.main_menu.main import launch
from client.globals.settings import Settings
from client.globals.window_size import WindowSize
from shared.loader import load_effects_names
from engine_antiantilopa import Vector2d
import pygame as pg

from client.widgets.sounds_load import load_sounds
from client.widgets.texture_load import load_textures

load_effects_names()

resolutions = [
    (1680, 1120),
    (1440, 960),
    (1200, 800),
    (960, 640),
    (720, 480),
    (600, 400),
]

try:
    Settings.get_from_file_()
except Exception as e:
    print("settings file cannot be read or it is nonexistent. default settings are used")
    print(e)
    gnm = None
    for res in resolutions:
        if res[0] < pg.display.Info().current_w and res[1] < pg.display.Info().current_h:
            gnm = res
            break
    if gnm is None:
        raise Exception("display is too small...")
    default_settings = {
        "resolution": gnm,
        "preffered_ipv4": "",
        "preffered_name": "",
        "texture_packs": ["default"],
        "preffered_color": 0
    }
    Settings.resolution.chosen = resolutions.index(default_settings["resolution"])
    Settings.pref_ipv4.var = default_settings["preffered_ipv4"]
    Settings.pref_name.var = default_settings["preffered_name"]
    Settings.texture_packs.order = default_settings["texture_packs"]
    Settings.preffered_color.chosen = default_settings["preffered_color"]
    
    Settings.save_to_file_()

WindowSize.value = Vector2d.from_tuple(Settings.resolution.variants[Settings.resolution.chosen])

load_textures(Settings.texture_packs.order)
load_sounds(Settings.texture_packs.order)

launch()
