from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.respondings.client import Client
from client.scenes.lobby_screen import scene as lobby_scene
from client.scenes.lobby_screen import init as lobby_init
from serializator.data_format import Format
import pygame as pg

scene = create_game_object(tags="main_menu", size=(1000, 1000))
GameObject.root.add_child(scene)

ip = None
name = None

def activate_entry(game_obj: GameObject, *_):
    game_obj.get_component(EntryComponent).active = True


label_obj = create_label(scene, "main_menu:main_label", text="Enter IPv4:", at=Position.CENTER, color=ColorComponent.RED)

box = create_game_object(scene, "main_menu:entry_box", at=(0, 100), size=Vector2d(500, 100), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, margin=Vector2d(50, 25), width=2)

entry_obj = create_game_object(box, "main_menu:entry", at=Position.CENTER, size=Vector2d(500, 100), color=ColorComponent.WHITE)
entry_obj.add_component(EntryComponent(active=True))

def cmd(*_):
    global label_obj, entry_obj, ip, name
    if ip is None:
        ip = entry_obj.get_component(EntryComponent).text
        entry_obj.get_component(EntryComponent).clear()
        label_obj.destroy()
        label_obj = create_label(scene, "main_menu:main_label", text="Enter nickname:", at=Position.CENTER, color=ColorComponent.RED)
        label_obj.first_iteration()
    elif name is None:
        name = entry_obj.get_component(EntryComponent).text
        lobby_init()
        c = Client.object
        c.init_client((ip, 9090))
        c.start()
        c.send(Format.event("LOBBY/JOIN", [name]))
        c.myname = name
        c.send(Format.request("LOBBY/NAMES", []))
        c.send(Format.request("LOBBY/READINESS", []))
        scene.disable()
        lobby_scene.enable()

button = create_game_object(scene, "main_menu:enter_button", at=(230, 100), size=(50, 50), color=ColorComponent.RED, shape=Shape.RECT)
button.add_component(OnClickComponent([1, 0, 0], 0, 0, cmd))
button.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, cmd))


scene.disable()

def launch():
    e = Engine(Vector2d(1200, 800))
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()