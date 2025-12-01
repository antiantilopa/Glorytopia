from engine_antiantilopa import *
from client.scenes.replay_screen import main as replay_main
from client.scenes.replay_screen import replay
from shared.globals.replay import RecordReplaySettings


def launch_replay_screen(replay_name: str):
    scene = GameObject.get_game_object_by_tags("choose_replay_menu")
    scene.disable()

    path = RecordReplaySettings.replay_path / replay_name
    replay.load(path)
    join_menu_scene = replay_main.load()
    replay_main.start()