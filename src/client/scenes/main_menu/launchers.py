from engine_antiantilopa import *
from client.globals.music import SoundManager

from client.network.client import GameClient
from client.scenes.join_menu import main  as join_menu_main
from client.scenes.choose_replay_menu import main as choose_replay_main
from client.scenes.lobby_screen import main as lobby_main
from client.scenes.game_screen import main as game_main
from netio.serialization.routing import MessageType
from shared.util.position import Pos


def launch_join_menu():
    scene = GameObject.get_game_object_by_tags("main_menu")
    scene.disable()
    join_menu_scene = join_menu_main.load()
    join_menu_scene.enable()

def launch_choose_replay_menu():
    scene = GameObject.get_game_object_by_tags("main_menu")
    scene.disable()
    choose_replay_scene = choose_replay_main.load()
    choose_replay_scene.enable()


