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

from shared.util.position import Pos

from . import ready_section
from . import launchers
from . import message_box

def main():

    router = GameClientRouter("LOBBY")

    @router.event("JOIN", datatype=None)
    def join(data: None):
        group = GameObject.get_group_by_tag("lobby_screen")
        if len(group) > 0 and group[0].active:
            ready_section.update_all_section()

    @router.event("DISCONNECT", datatype=str)
    def disconnect(nickname: str):
        pdata = [pdata for pdata in GamePlayer.joined_players if pdata.nickname == nickname]
        if len(pdata) == 0:
            return
        pdata = pdata[0]
        if pdata.joined and pdata in GamePlayer.joined_players:
            GamePlayer.joined_players.remove(pdata)

        group = GameObject.get_group_by_tag("lobby_screen")
        if len(group) > 0 and group[0].active:
            ready_section.update_all_section()

    @router.event("READY", datatype=None)
    def ready(data: None):
        group = GameObject.get_group_by_tag("lobby_screen")
        if len(group) > 0 and group[0].active:
            ready_section.update_ready()

    @router.event("COLOR_CHANGE", datatype=None)
    def color_change(data: None):
        print("!!!\t", GamePlayer.joined_players)
        group = GameObject.get_group_by_tag("lobby_screen")
        if len(group) > 0 and group[0].active:
            ready_section.update_all_section()
        
    @router.event("MESSAGE", datatype=tuple[str, str])
    def message(message: tuple[str, str]):
        message_box.Messages.messages.append(message)
        group = GameObject.get_group_by_tag("lobby_screen")
        if len(group) > 0 and group[0].active:
            message_box.update_messages()

    @router.event("GAME_START", datatype=tuple[int, Pos])
    def game_start(data: tuple[int, Pos]):
        launchers.launch_game_screen(*data)