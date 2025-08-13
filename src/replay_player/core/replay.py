from replay_player.core.frame import Frame
from server.core.game import Game, SerializedGame
from server.core.game_event import GameEvent
from server.core.unit import SerializedUnit_, Unit
from server.core.updating_object import UpdatingObject
from shared.unit import UnitData


class Replay:
    game: Game
    initial_state: SerializedGame
    frames: list[Frame]
    current_frame: int
    watch_as: int

    obj: "Replay" = None
    colors = [
        ((255, 0, 0), (255, 255, 255)),   # Red - White
        ((0, 255, 0), (0, 0, 0)),   # Green
        ((0, 0, 255), (255, 255, 255)),   # Blue - White
        ((255, 255, 0), (0, 0, 0)),   # Yellow - Black
        ((255, 165, 0), (0, 0, 0)),   # Orange - Black
        ((128, 0, 128), (255, 255, 255)),   # Purple - White
        ((192, 192, 192), (0, 0, 0)),   # Silver - Black
        ((0, 128, 128), (255, 255, 255)),   # Teal - White
    ]
    def __init__(self, game: Game, serialized_game: SerializedGame, frames: list[Frame]):
        self.game = game
        self.initial_state = serialized_game
        self.frames = frames
        self.current_frame = -1
        self.watch_as = 0

        Replay.obj = self
    
    def next_frame(self):
        self.current_frame += 1
        changes = self.frames[self.current_frame].changes
        func_name = "Unknown"
        for name in GameEvent.event_ids:
            if GameEvent.event_ids[name] == self.frames[self.current_frame].func:
                func_name = name
                break
        for change in changes:
            UpdatingObject.sub_clss[change.cls_id].do_serializable(change.cls_serialized)
        print(f"{self.current_frame + 1}/{len(self.frames)}")
