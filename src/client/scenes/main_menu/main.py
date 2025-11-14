from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.globals.settings import Settings
from client.globals.music import SoundManager
from client.globals.window_size import WindowSize
from client.network.client import GameClient

import pygame as pg

from . import launchers

def load():
    if len(GameObject.get_group_by_tag("main_menu")) > 0:
        return GameObject.get_game_object_by_tags("main_menu")

    scene = create_game_object(tags="main_menu", size=WindowSize.value)

    join_button = create_game_object(
        parent=scene,
        tags="main_menu:join_button",
        at=InGrid((12, 8), (4, 3), (4, 1)),
        color=ColorComponent.RED,
        shape=Shape.RECT,
        margin=Vector2d(5, 5)
    )
    create_label(
        parent=join_button,
        tags="main_menu:join_button:label",
        color=ColorComponent.WHITE,
        text="join lobby",
    )
    join_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda*_: launchers.launch_join_menu()))
    join_button.add_component(KeyBindComponent([pg.K_RETURN], 0, 1, lambda*_: launchers.launch_join_menu()))

    replay_button = create_game_object(
        parent=scene,
        tags="main_menu:replay_button",
        at=InGrid((12, 8), (4, 4), (4, 1)),
        color=ColorComponent.BLUE,
        shape=Shape.RECT,
        margin=Vector2d(5, 5)
    )
    create_label(
        parent=replay_button,
        tags="main_menu:replay_button:label",
        color=ColorComponent.WHITE,
        text="watch replay (TODO)",
    )
    replay_button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda*_: launchers.launch_choose_replay_menu()))

    scene.disable()
    return scene

def launch():
    scene = load()
    e = Engine(WindowSize.value)
    scene.enable()
    e.run()
