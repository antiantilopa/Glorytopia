from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.globals.settings import Settings
from client.globals.music import SoundManager
from client.globals.window_size import WindowSize
from client.network.client import GameClient

import pygame as pg
from netio.serialization.routing import MessageType

from .state import State
from . import launchers
from . import states
from . import network

states.main()
network.main()

def load():
    if len(GameObject.get_group_by_tag("join_menu")) > 0:
        return GameObject.get_game_object_by_tags("join_menu")

    scene = create_game_object(tags="join_menu", size=WindowSize.value)
    SoundManager.new_music("melody1")
    
    settings_button = create_game_object(
        parent=scene, 
        tags="join_menu:settings_button", 
        at=Position.LEFT_DOWN, 
        size=Vector2d(210, 70), 
        surface_margin=Vector2d(10, 10), 
        color=ColorComponent.BLUE, 
        shape=Shape.RECT
    )
    create_label(
        parent=settings_button, 
        tags="join_menu:settings_button:label", 
        text="Settings", 
        color=ColorComponent.WHITE
    )

    settings_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda *_: launchers.launch_settings_menu()))

    label_obj = create_label(
        parent=scene, 
        tags="join_menu:main_label", 
        text="Enter IPv4:", 
        at=Position.CENTER, 
        color=ColorComponent.RED
    )

    box = create_game_object(scene, "join_menu:entry_box", at=(0, 100), size=Vector2d(500, 100), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, margin=Vector2d(50, 25), width=2)

    entry_obj = create_game_object(box, "join_menu:entry_box:entry", at=Position.CENTER, size=Vector2d(500, 100), color=ColorComponent.WHITE)
    entry_obj.add_component(EntryComponent(default_text=Settings.pref_ipv4.var, active=True))

    button = create_game_object(scene, "join_menu:enter_button", at=(230, 100), size=(50, 50), color=ColorComponent.RED, shape=Shape.RECT)
    button.add_component(OnClickComponent([1, 0, 0], 0, 0, cmd))
    button.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, cmd))

    scene.disable()

    return scene

def connect():
    entry_obj = GameObject.get_game_object_by_tags("join_menu:entry_box:entry")

    ip = entry_obj.get_component(EntryComponent).text
    try:
        GameClient(ip, 8080)
    except Exception as e:
        print(f"Failed to connect to server at {ip}: {e}")
        entry_obj.get_component(EntryComponent).clear()
        ip = None
        return
    State.change_state(1)

def join():
    entry_obj = GameObject.get_game_object_by_tags("join_menu:entry_box:entry")

    name = entry_obj.get_component(EntryComponent).text
    GameClient.object.send_message(MessageType.REQUEST, "LOBBY/JOIN", name)

def reconnect():
    entry_obj = GameObject.get_game_object_by_tags("join_menu:entry_box:entry")

    try:
        recovery_code = int(entry_obj.get_component(EntryComponent).text)
    except ValueError:
        print("Recovery code must be a 6-digit integer.")
        return
    if recovery_code < 100000 or recovery_code > 999999:
        recovery_code = None
        print("Recovery code must be a 6-digit integer.")
        return
    entry_obj.get_component(EntryComponent).clear()
    GameClient.object.send_message(MessageType.REQUEST, "LOBBY/RECONNECT", recovery_code)

def cmd(*_):
    match State.value:
        case 0: connect()
        case 1: join()
        case 2: reconnect()

def launch():
    scene = load()
    e = Engine(WindowSize.value)
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()