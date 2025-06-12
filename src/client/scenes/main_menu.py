from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.respondings.client import Client
from client.scenes.lobby_screen import load as lobby_load
from client.scenes.lobby_screen import init as lobby_init
from serializator.data_format import Format
import pygame as pg

ip = None
name = None

def load(screen_size: Vector2d = Vector2d(1200, 800)):
    scene = create_game_object(tags="main_menu", size=screen_size)

    def activate_entry(game_obj: GameObject, *_):
        game_obj.get_component(EntryComponent).active = True

    label_obj = create_label(scene, "main_menu:main_label", text="Enter IPv4:", at=Position.CENTER, color=ColorComponent.RED)

    box = create_game_object(scene, "main_menu:entry_box", at=(0, 100), size=Vector2d(500, 100), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, margin=Vector2d(50, 25), width=2)

    entry_obj = create_game_object(box, "main_menu:entry_box:entry", at=Position.CENTER, size=Vector2d(500, 100), color=ColorComponent.WHITE)
    entry_obj.add_component(EntryComponent(default_text="26.220.113.32", active=True))

    def cmd(*_):
        global ip, name
        if ip is None:
            ip = entry_obj.get_component(EntryComponent).text
            entry_obj.get_component(EntryComponent).clear()
            label_obj.destroy()
            new_label_obj = create_label(scene, "main_menu:main_label", text="Enter nickname:", at=Position.CENTER, color=ColorComponent.RED)
            new_label_obj.first_iteration()
        elif name is None:
            name = entry_obj.get_component(EntryComponent).text
            launch_lobby()

    def launch_lobby():
        global ip, name
        scene.disable()
        lobbby_scene = lobby_load(screen_size)
        lobby_init()
        lobbby_scene.enable()

        c = Client.object
        c.myname = name
        c.init_client((ip, 9090))
        c.start()
        c.send(Format.event("LOBBY/JOIN", [name]))
        c.send(Format.request("LOBBY/NAMES", []))
        c.send(Format.request("LOBBY/READINESS", []))

    button = create_game_object(scene, "main_menu:enter_button", at=(230, 100), size=(50, 50), color=ColorComponent.RED, shape=Shape.RECT)
    button.add_component(OnClickComponent([1, 0, 0], 0, 0, cmd))
    button.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, cmd))

    scene.disable()

    return scene

def launch():
    load()
    scene = GameObject.get_group_by_tag("main_menu")[0]

    e = Engine(Vector2d(1200, 800))
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()