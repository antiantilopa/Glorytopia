from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.globals.settings import Settings
from client.network.client import GameClient
from client.scenes.settings_change_menu import load as settings_change_load
from client.widgets.sounds_load import load_sounds
from client.widgets.sound import SoundComponent
from client.widgets.texture_load import load_textures
import pygame as pg

from . import enter_name

def load(screen_size: Vector2d = Vector2d(1200, 800)):
    if len(GameObject.get_group_by_tag("main_menu")) > 0:
        return GameObject.get_game_object_by_tags("main_menu")
    
    load_textures(Settings.texture_packs.order)
    load_sounds(Settings.texture_packs.order)

    scene = create_game_object(tags="main_menu", size=screen_size)
    scene.add_component(SoundComponent(nickname="melody1"))
    scene.get_component(SoundComponent).play_in_loop()
    
    settings_button = create_game_object(scene, "main_menu:settings_button", Position.LEFT_DOWN, size=Vector2d(210, 70), surface_margin=Vector2d(10, 10), color=ColorComponent.BLUE, shape=Shape.RECT)
    create_label(
        parent=settings_button, 
        tags="main_menu:settings_button:label", 
        text="Settings", 
        color=ColorComponent.WHITE
    )

    settings_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda *_: launch_settings_menu()))

    label_obj = create_label(
        parent=scene, 
        tags="main_menu:main_label", 
        text="Enter IPv4:", 
        at=Position.CENTER, 
        color=ColorComponent.RED
    )

    box = create_game_object(scene, "main_menu:entry_box", at=(0, 100), size=Vector2d(500, 100), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, margin=Vector2d(50, 25), width=2)

    entry_obj = create_game_object(box, "main_menu:entry_box:entry", at=Position.CENTER, size=Vector2d(500, 100), color=ColorComponent.WHITE)
    entry_obj.add_component(EntryComponent(default_text=Settings.pref_ipv4.var, active=True))

    button = create_game_object(scene, "main_menu:enter_button", at=(230, 100), size=(50, 50), color=ColorComponent.RED, shape=Shape.RECT)
    button.add_component(OnClickComponent([1, 0, 0], 0, 0, cmd))
    button.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, cmd))

    scene.disable()


    def cmd(*_):
        ip = entry_obj.get_component(EntryComponent).text
        try:
            GameClient(ip, 8080)
        except Exception as e:
            print(f"Failed to connect to server at {ip}: {e}")
            entry_obj.get_component(EntryComponent).clear()
            return
        entry_obj.get_component(EntryComponent).clear()
        entry_obj.get_component(EntryComponent).text = Settings.pref_name.var
        label_obj.destroy()
        new_label_obj = create_label(
            parent=scene, 
            tags="main_menu:main_label", 
            text="Enter nickname:", 
            at=Position.CENTER, 
            color=ColorComponent.RED
        )
        new_label_obj.first_iteration()

    def launch_settings_menu():
        scene.disable()
        settings_menu_scene = settings_change_load(screen_size)
        settings_menu_scene.enable()

    def launch_enter_name():
        scene.destroy() # no need to destroy...
        enter_name.load(screen_size).enable()
    
    return scene