import os
from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from client.globals.settings import Settings
from client.globals.music import SoundManager
from client.globals.window_size import WindowSize
from client.network.client import GameClient

import pygame as pg

from shared.globals.replay import RecordReplaySettings

from . import launchers

def load():
    if len(GameObject.get_group_by_tag("choose_replay_menu")) > 0:
        return GameObject.get_game_object_by_tags("choose_replay_menu")

    scene = create_game_object(tags="choose_replay_menu", size=WindowSize.value)

    file_list = create_list_game_object(
        parent=scene, 
        tags="choose_replay_menu:file_list", 
        at=InGrid((1, 1), (0, 0)), 
        surface_margin=Vector2d(20, 20),
        speed=Vector2d(0, 30)
    )

    replays = os.listdir(RecordReplaySettings.replay_path)
    for i in range(len(replays)):
        file_obj = create_game_object(
            parent=file_list, 
            tags="choose_replay_menu:file_list:file", 
            at=InGrid((1, 8), (0, i))
        )
        create_game_object(
            parent=file_obj,
            tags="choose_replay_menu:file_list:file:box",
            at=InGrid((1, 1), (0, 0)),
            color=ColorComponent.WHITE,
            shape=Shape.RECTBORDER,
            width=2,
            surface_margin=Vector2d(2, 2)
        )
        create_label(
            color=ColorComponent.RED, 
            parent=file_obj, 
            tags="choose_replay_menu:file_list:file:name", 
            text=str(replays[i]), 
            font=pg.font.SysFont("consolas", WindowSize.value.inty() // 20), 
            at=Position.LEFT, 
            margin=Vector2d(5, 0)
        )
        button = create_game_object(
            parent=file_obj,
            tags="choose_replay_menu:file_list:file:select_button",
            at=Position.RIGHT,
            size=(WindowSize.value // (Vector2d(12, 8) * 1.5)),
            color=ColorComponent.GREEN,
            shape=Shape.RECT,
            surface_margin=Vector2d(7, 0)
        )
        button.add_component(OnClickComponent([1, 0, 0], 0, 1, lambda g, k, p, *args: launchers.launch_replay_screen(args[0]), replays[i]))

    scene.disable()
    return scene

def launch():
    scene = load()
    e = Engine(WindowSize.value)
    scene.enable()
    e.run()
