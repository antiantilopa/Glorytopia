from engine_antiantilopa import *
from replay_player.widgets.fastgameobjectcreator import *
from server.globals.replay import RecordReplaySettings
from replay_player.core.load import load as load_replay
from .watch_replay import load as load_watch
from .watch_replay import load as start_watch
import os

def load(screen_size: Vector2d = Vector2d(1200, 800)):
    if len(GameObject.get_group_by_tag("select_file")) > 0:
        return GameObject.get_game_object_by_tags("select_file")

    scene = create_game_object(
        tags="select_file", 
        size=screen_size
    )

    file_list = create_list_game_object(
        parent=scene, 
        tags="select_file:file_list", 
        at=InGrid((1, 1), (0, 0)), 
        surface_margin=Vector2d(20, 20),
        speed=Vector2d(0, 30)
    )

    replays = os.listdir(RecordReplaySettings.replay_path)
    for i in range(len(replays)):
        file_obj = create_game_object(
            parent=file_list, 
            tags="select_file:file_list:file", 
            at=InGrid((1, 8), (0, i))
        )
        create_game_object(
            parent=file_obj,
            tags="select_file:file_list:file:box",
            at=InGrid((1, 1), (0, 0)),
            color=ColorComponent.WHITE,
            shape=Shape.RECTBORDER,
            width=2,
            surface_margin=Vector2d(2, 2)
        )
        create_label(
            color=ColorComponent.RED, 
            parent=file_obj, 
            tags="select_file:file_list:file:name", 
            text=str(replays[i]), 
            font=pg.font.SysFont("consolas", screen_size.y // 20), 
            at=Position.LEFT, 
            margin=Vector2d(5, 0)
        )
        button = create_game_object(
            parent=file_obj,
            tags="select_file:file_list:file:select_button",
            at=Position.RIGHT,
            size=(screen_size // (Vector2d(12, 8) * 1.5)),
            color=ColorComponent.GREEN,
            shape=Shape.RECT,
            surface_margin=Vector2d(7, 0)
        )
        button.add_component(OnClickComponent([1, 0, 0], 0, 1, select_file, replays[i]))

    scene.disable()
    return scene

def select_file(g, k, p, *args: tuple[str]):
    replay = load_replay(*args)
    print("loading new scene? I mean, it should be it")
    scene = GameObject.get_game_object_by_tags("select_file")
    scene.disable()
    load_watch(screen_size=scene.get_component(SurfaceComponent).size)
    start_watch()

def launch(screen_size: Vector2d = Vector2d(1200, 800)):
    load(screen_size)
    scene = GameObject.get_group_by_tag("select_file")[0]

    e = Engine(screen_size)
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()