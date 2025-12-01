from engine_antiantilopa import *
from client.globals.window_size import WindowSize
from client.network.client import GameClient, GamePlayer
from client.globals.settings import Settings
from client.scenes.lobby_screen import message_box
from client.widgets.fastgameobjectcreator import *
from client.widgets.sound import SoundComponent
from shared.asset_types import Nation
from netio import MessageType
import threading
import pygame as pg

from . import launchers
from . import network
from . import ready_section

network.main()

def load():
    scene = create_game_object(tags="lobby_screen", size=WindowSize.value)
    
    chat_section = create_game_object(scene, "lobby_screen:chat_section", at=InGrid((12, 8), (6, 0), (6, 8)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    message_section = create_game_object(chat_section, "lobby_screen:chat_section:message_section", at=InGrid((1, 10), (0, 0), (1, 9)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)
    
    message_section.add_component(KeyBindComponent([pg.K_UP, pg.K_DOWN], 0, 1, message_box.scroll))
    
    entry_box = create_game_object(chat_section, "lobby_screen:chat_section:entry_box", at=InGrid((1, 10), (0, 9), (1, 1)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, margin=Vector2d(6, 6))
    
    entry_obj = create_game_object(entry_box, "lobby_screen:chat_section:entry_box:entry", at=InGrid((1, 1), (0, 0), (1, 1)), color=ColorComponent.RED, margin=Vector2d(2, 2))
    entry_obj.add_component(EntryComponent(active=True, font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40)))
    entry_obj.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, send_message))

    ready_section_obj = create_game_object(scene, "lobby_screen:ready_section", at=InGrid((12, 8), (0, 0), (6, 3)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)
    info_section = create_game_object(scene, "lobby_screen:info_section", at=InGrid((12, 8), (0, 3), (6, 5)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2)

    ready_button = create_game_object(info_section, "lobby_screen:info_section:ready_button", Position.LEFT_UP, Vector2d(70, 70), ColorComponent.RED, Shape.RECT, margin=Vector2d(10, 10))
    ready_button.add_component(OnClickComponent([1, 0, 0], 0, 1, send_ready))

    ready_button_label = create_label(
        parent=ready_button, 
        tags="lobby_screen:info_section:ready_button:label", text="Ready", 
        font=pg.font.SysFont("consolas", 20), 
        color=ColorComponent.WHITE
    )

    color_change_box = create_list_game_object(
        parent=info_section,
        tags="lobby_screen:info_section:color_change_box",
        at=InGrid((6, 5), (0, 1), (6, 1)),
        color=ColorComponent.WHITE,
        shape=Shape.RECTBORDER,
        surface_margin=Vector2d(2, 2),
        width=2,
        axis=(1, 0),
    )

    for i, color in enumerate(GamePlayer.colors):
        color_change_button = create_game_object(color_change_box, "lobby_screen:info_section:color_change_box:button", InGrid((8, 1), (i, 0), (1, 1)), color=color[0], shape=Shape.RECT, margin=Vector2d(5, 5))
        color_change_button.add_component(OnClickComponent([1, 0, 0], 0, 1, send_change_color, i))
        color_change_button_label = create_label(
            parent=color_change_button, 
            tags=["lobby_screen:info_section:change_color_box:button:label", f"{i}"], 
            text="O", 
            font=pg.font.SysFont("consolas", WindowSize.value.inty() // 12), 
            color=color[1]
        )
    
    nation_change_box = create_list_game_object(
        parent=info_section,
        tags="lobby_screen:info_section:nation_change_box",
        at=InGrid((6, 5), (0, 2), (6, 1)),
        color=ColorComponent.WHITE,
        shape=Shape.RECTBORDER,
        surface_margin=Vector2d(2, 2),
        width=2,
        axis=(1, 0)
    )
    
    for i, nation in enumerate(Nation.values()):
        nation_change_button = create_game_object(
            parent=nation_change_box, 
            tags="lobby_screen:info_section:nation_change_box:button", 
            at=InGrid((8, 1), (i, 0), (1, 1)), 
            color=(255, 255, 255), 
            shape=Shape.RECT, 
            margin=Vector2d(5, 5)
        )
        nation_change_button.add_component(OnClickComponent([1, 0, 0], 0, 1, send_change_nation, nation.id))
        nation_change_button_icon = create_game_object(
            parent=nation_change_button, 
            tags=["lobby_screen:info_section:change_nation_box:button:icon", f"{i}"], 
            size=WindowSize.get_block_size() * (2 / 3)
        )
        print(nation.name)
        nation_change_button_icon.add_component(SpriteComponent(nickname=nation.name, size=WindowSize.get_block_size() * (2 / 3)))

    ready_section.update_all_section()
    scene.disable()
    return scene




def send_message(g_obj: GameObject, *_):
        text = g_obj.get_component(EntryComponent).text
        GameClient.object.send_message(MessageType.EVENT, "LOBBY/MESSAGE", text)
        g_obj.get_component(EntryComponent).clear()

def send_ready(*_):
    GameClient.object.send_message(MessageType.EVENT, "LOBBY/READY", (1 - GameClient.object.me.is_ready))

def send_change_color(g, k, p, i):
    GameClient.object.send_message(MessageType.EVENT, "LOBBY/COLOR_CHANGE", i)

def send_change_nation(g, k, p, i):
    GameClient.object.send_message(MessageType.EVENT, "LOBBY/NATION_CHANGE", i)


def launch():
    GameObject.get_game_object_by_tags("lobby_screen").enable()
    e = Engine(Vector2d(1200, 800))
    e.run()
    exit()

if __name__ == "__main__":
    load()
    launch()