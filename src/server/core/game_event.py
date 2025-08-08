import os
from . import player as Player
from shared.error_codes import ErrorCodes
from .updating_object import UpdatingObject
from typing import Callable
from server.globals.mod_versions import ModVersions
from server.globals.replay import RecordReplaySettings
from serializator.net import Serializator
from engine_antiantilopa import Vector2d

def to_serializable(obj):
    if hasattr(obj, "to_serializable"):
        return obj.to_serializable()
    if isinstance(obj, int|float|str|bool|None):
        return obj
    if isinstance(obj, list|tuple):
        return [to_serializable(item) for item in obj]
    if isinstance(obj, Vector2d):
        return obj.as_tuple()
    if hasattr(obj, "id"):
        return obj.id
    


class GameEvent:
    initialized: bool = False
    event_ids: dict[str, int] = {}
    ID = 0

    @staticmethod
    def game_event(func: Callable) -> Callable:
        GameEvent.event_ids[func.__name__] = GameEvent.ID
        GameEvent.ID += 1
        def wrapper(self: "Player.Player", *args, **kwargs):
            if len(UpdatingObject.updated_objs) > 0:
                print(f"WTF!!! called {func.__name__} but should not")
            result = func(self, *args, **kwargs)
            if result == ErrorCodes.SUCCESS:
                GameEvent.record_event(self, func.__name__, *args)
            return result
        return wrapper
        
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