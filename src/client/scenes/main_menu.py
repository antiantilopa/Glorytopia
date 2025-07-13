from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.globals.settings import Settings
from client.respondings.client import Client
from client.scenes.lobby_screen import load as lobby_load
from client.scenes.lobby_screen import init as lobby_init
from client.scenes.settings_change_menu import load as settings_change_load
from client.widgets.sounds_load import load_sounds
from client.widgets.sound import SoundComponent
from serializator.data_format import Format
from client.respondings.client import UpdateCodes
import pygame as pg
from . import game_screen
import threading

ip = None
name = None
recovery_code = None

def load(screen_size: Vector2d = Vector2d(1200, 800)):
    if len(GameObject.get_group_by_tag("main_menu")) > 0:
        return GameObject.get_game_object_by_tags("main_menu")

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

    def cmd(*_):
        global ip, name, recovery_code
        if ip is None:
            ip = entry_obj.get_component(EntryComponent).text
            try:
                c = Client.object
                c.init_client((ip, 9090))
                c.start()
                c.send(Format.request("LOBBY/NAMES", []))
                settings_button.destroy()
            except Exception as e:
                print(f"Failed to connect to server at {ip}: {e}")
                entry_obj.get_component(EntryComponent).clear()
                ip = None
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
        elif name is None:
            name = entry_obj.get_component(EntryComponent).text
            c = Client.object
            c.myname = name
            Client.object.send(Format.event("LOBBY/JOIN", [name]))
            while Client.object.joined is None:
                pass
            if Client.object.joined:
                launch_lobby()
            else:
                Client.object.joined = None
                entry_obj.get_component(EntryComponent).clear()
                GameObject.get_game_object_by_tags("main_menu:main_label").destroy()
                new_label_obj = create_label(
                    parent=scene, 
                    tags="main_menu:main_label", 
                    text="Enter recovery code:", 
                    at=Position.CENTER, 
                    color=ColorComponent.RED
                )
                new_label_obj.first_iteration()
        elif recovery_code is None:
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
            Client.object.send(Format.event("LOBBY/RECONNECT", [name, recovery_code]))
            while Client.object.joined is None:
                pass
            if not Client.object.joined:
                recovery_code = None
                print("Failed to reconnect. Please check your recovery code.")
                return
            else:
                Client.object.send(Format.request("LOBBY/NAMES", []))
                Client.object.send(Format.request("ORDER", []))
                Client.object.send(Format.request("LOBBY/COLORS", []))
                Client.object.send(Format.request("GAME/NOW_PLAYING_PLAYER_INDEX", []))
                print("Reconnected successfully.")
                GameObject.get_game_object_by_tags("main_menu").disable()
                Client.object.game_started = True
                while not (Client.object.updated & 2 ** UpdateCodes.INIT_COLORS.value):
                    pass
                threading.Thread(target=start_game).start()

    def launch_settings_menu():
        scene.disable()
        settings_menu_scene = settings_change_load(screen_size)
        settings_menu_scene.enable()

    def launch_lobby():
        global ip, name
        scene.disable()
        lobbby_scene = lobby_load(screen_size)
        lobby_init()
        lobbby_scene.enable()

        c = Client.object
        c.send(Format.request("LOBBY/NAMES", []))
        c.send(Format.request("ORDER", []))
        c.send(Format.request("LOBBY/COLORS", []))
        c.send(Format.request("LOBBY/READINESS", []))
    
    def start_game():
        scene = GameObject.get_group_by_tag("main_menu")[0]
        scene.get_component(SoundComponent).stop_all_channels()
        scene.disable()
        self = Client.object
        self.game_started = True
        self.send(Format.request("GAME/WORLD_SIZE", []))
        self.send(Format.request("GAME/WORLD", []))
        self.send(Format.request("GAME/CITIES", []))
        self.send(Format.request("GAME/UNITS", []))
        self.send(Format.request("GAME/MY_MONEY", []))
        self.send(Format.request("GAME/MY_TECHS", []))
        self.updated |= 2 ** UpdateCodes.GAME_START.value
        game_scene = game_screen.load(scene.get_component(SurfaceComponent).size)
        game_screen.init()
        game_screen.start()

    button = create_game_object(scene, "main_menu:enter_button", at=(230, 100), size=(50, 50), color=ColorComponent.RED, shape=Shape.RECT)
    button.add_component(OnClickComponent([1, 0, 0], 0, 0, cmd))
    button.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, cmd))

    scene.disable()

    return scene

def launch(screen_size: Vector2d = Vector2d(1200, 800)):
    load(screen_size)
    scene = GameObject.get_group_by_tag("main_menu")[0]

    e = Engine(screen_size)
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()