from engine_antiantilopa import *
from client.scenes.join_menu import main

def launch_join_menu():
    scene = GameObject.get_game_object_by_tags("settings_screen")
    scene.destroy()
    join_menu_scene = main.load()
    join_menu_scene.enable()
