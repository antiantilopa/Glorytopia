from engine_antiantilopa import *

from client.scenes.join_menu import main  as join_menu_main
from client.scenes.choose_replay_menu import main as choose_replay_main
from client.scenes.settings_change_menu import main as settings_change_main

def launch_settings_menu():
    scene = GameObject.get_game_object_by_tags("main_menu")
    scene.disable()
    settings_menu_scene = settings_change_main.load()
    settings_menu_scene.enable()

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


