from engine_antiantilopa import *
from client.network.client import GameClient, GameClientRouter, GamePlayer
from client.globals.settings import Settings
from client.widgets.fastgameobjectcreator import *
from client.widgets.sound import SoundComponent
from shared.asset_types import Nation
from netio import MessageType
from client.globals.window_size import WindowSize
import threading
import pygame as pg

from . import launchers


class Messages:
    messages: list[tuple[str, str]] = []
    scroll_num = 0

def update_messages():
    message_section = GameObject.get_group_by_tag("lobby_screen:chat_section:message_section")[0]
    message_section.disable()
    for child in message_section.childs:
        child.get_component(Transform).move(Vector2d(0, -(message_section.get_component(SurfaceComponent).size.y // 15)))
    for i in range(len(message_section.childs), len(Messages.messages)):
        n = create_game_object(message_section, "lobby_screen:chat_section:mesage_section:message_box", at=InGrid((1, 15), (0, 14)), color=ColorComponent.WHITE, shape=Shape.RECTBORDER, width=2, margin = Vector2d(3, 3))
        color = ColorComponent.WHITE
        l = create_label(
            parent=n, 
            tags="lobby_screen:chat_section:mesage_section:message_box:message_label", 
            at=Position.LEFT, 
            text=f"{Messages.messages[i][0]}: {Messages.messages[i][1]}", 
            font=pg.font.SysFont("consolas", WindowSize.value.inty() // 40), 
            color=color, 
            margin=Vector2d(10, 2)
        )
    message_section.enable()

def scroll(g_obj: GameObject, tr: list[int], *_):
    if len(tr) != 1:
        return
    dy = 1 if tr[0] == pg.K_UP else -1
    if Messages.scroll_num + dy < 0 or Messages.scroll_num + dy + 15 > len(Messages.messages):
        return
    g_obj.disable()
    for child in g_obj.childs:
        child.get_component(Transform).move(Vector2d(0, g_obj.get_component(SurfaceComponent).size.y // 15 * dy))
    Messages.scroll_num += dy
    g_obj.enable()
