from engine_antiantilopa import *
from client.globals.music import SoundManager

from client.network.client import GameClient
from client.scenes.settings_change_menu import main as settings_change_main
from client.scenes.lobby_screen import main as lobby_main
from client.scenes.game_screen import main as game_main
from netio.serialization.routing import MessageType
from shared.util.position import Pos


def launch_settings_menu():
    scene = GameObject.get_game_object_by_tags("join_menu")
    scene.disable()
    settings_menu_scene = settings_change_main.load()
    settings_menu_scene.enable()

def launch_game_screen(now_playing_player_id: int, world_size: Pos):
    GameClient.object.me.money = 0
    GameClient.object.me.techs = []
    GameClient.object.send_message(MessageType.REQUEST, "GAME/MONEY", None)
    GameClient.object.send_message(MessageType.REQUEST, "GAME/TECHS", None)
    scene = GameObject.get_game_object_by_tags("join_menu")
    scene.destroy()
    SoundManager.stop_music()
    game_main.init(now_playing_player_id, world_size)
    game_main.load()
    game_main.start()

def launch_lobby():
    scene = GameObject.get_game_object_by_tags("join_menu")
    scene.destroy()
    lobbby_scene = lobby_main.load()
    lobbby_scene.enable()