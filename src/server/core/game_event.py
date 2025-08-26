import os
from . import player as Player
from shared.error_codes import ErrorCodes
from typing import Callable
from shared.globals.mod_versions import ModVersions
from server.globals.replay import RecordReplaySettings
from engine_antiantilopa import Vector2d

class GameEvent:
    initialized: bool = False
    event_ids: dict[str, int] = {}
    ID = 0
        
    @staticmethod
    def start_recording() -> None:
        if RecordReplaySettings.record_replay.chosen == 0:
            return
        if not os.path.exists(RecordReplaySettings.replay_path):
            os.mkdir(RecordReplaySettings.replay_path)
        data = to_serializable(ModVersions.mods)
        with open(f"../replays/{RecordReplaySettings.replay_file_name}.replay", "wb") as f:
            f.write(Serializator.encode(data))

    @staticmethod
    def record_event(self: "Player.Player", func_name: str, *args) -> None:
        if RecordReplaySettings.record_replay.chosen == 0:
            return
        if not os.path.exists(RecordReplaySettings.replay_path):
            os.mkdir(RecordReplaySettings.replay_path)
        if not os.path.exists(f"../replays/{RecordReplaySettings.replay_file_name}.replay"):
            raise FileNotFoundError(f"Replay file {RecordReplaySettings.replay_file_name}.replay does not exist")
        if GameEvent.initialized == False:
            from .game import Game
            # I am very sorry for doing so. I just do not want to make all imports look strange as
            # from . import something
            GameEvent.initialized = True
            data = Game.obj.to_serializable()
            with open(f"../replays/{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
                f.write(Serializator.encode(data))
        data = [self.id, GameEvent.event_ids[func_name], to_serializable(args), []]
        for obj in UpdatingObject.updated_objs:
            data[3].append([UpdatingObject.sub_clss.index(type(obj)), obj.to_serializable()])
        with open(f"../replays/{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(Serializator.encode(data))