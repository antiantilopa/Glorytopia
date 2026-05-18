from engine_antiantilopa import *
from client.scenes.main_menu import main

def launch_main_menu():
    scene = GameObject.get_game_object_by_tags("settings_screen")
    scene.destroy()
    main_menu_scene = main.load()
    main_menu_scene.enable()
