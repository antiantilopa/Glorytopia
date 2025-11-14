from io import BufferedWriter
from math import ceil
import os

from netio.serialization.serializer import SpecialTypes, SerializationTypes
from server.core.city import City
from server.core.game import Game
from server.core.tile import Tile
from server.core.unit import Unit
from server.core.world import World
from shared.player import PlayerData_
from .player import Player
from shared.error_codes import ErrorCodes
from typing import Callable
from shared.globals.mod_versions import ModVersions
from shared.globals.replay import RecordReplaySettings
from netio import Serializable, BaseWriter

def to_bytes(obj) -> bytes:
    return GameEvent.writer._any_to_bytes(obj)

class GameEvent:
    initialized: bool = False
    writer = BaseWriter()
    prev_now_plaing_player_id: int = 0
        
    @staticmethod
    def start_recording() -> None:
        if RecordReplaySettings.record_replay.chosen == 0:
            return
        if not os.path.exists(RecordReplaySettings.replay_path):
            os.mkdir(RecordReplaySettings.replay_path)
        if not os.path.exists(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay"):
            with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "wb") as f:
                f.write(bytes([SerializationTypes.LIST.value]))
            GameEvent.record_mods()
            GameEvent.record_game_data()
            GameEvent.record_player_datas([p.pdata for p in Player.players])
            GameEvent.record_world()
            GameEvent.record_objects()
            GameEvent.record_players(Player.players)
            with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
                f.write(bytes([SerializationTypes.END_OF_OBJECT.value]))
        GameEvent.initialized = 1

    @staticmethod
    def record_mods():
        data = to_bytes(ModVersions.mods)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data)

    @staticmethod
    def record_player_datas(player_datas: list[PlayerData_]):
        data = to_bytes(player_datas)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data)

    @staticmethod
    def record_players(players: list[Player]):
        player_datas = []
        for player in players:
            flat_vision = [item for sublist in player.vision for item in sublist]
            player_datas.append((player.id, player.money, player.techs, list_bool_to_list_int32(flat_vision)))
        data = to_bytes(player_datas)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data)

    @staticmethod
    def record_game_data():
        game = Game.obj
        game_data = (game.world.size, len(game.players), game.now_playing_player_index)
        GameEvent.prev_now_plaing_player_id = game.now_playing_player_index
        data = to_bytes(game_data)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data)

    @staticmethod
    def record_world():
        # HACK wtf r ya doin? can save a buncha memory! 
        # essentially, it is because every tile has its position stored. 
        world_data = []
        for row in Game.obj.world.world:
             for tile in row:
                world_data.append(tile)
        data = to_bytes(world_data)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data)
    
    @staticmethod
    def record_objects():
        units = Unit.units
        cities = City.cities
        data1 = to_bytes(units)
        data2 = to_bytes(cities)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data1)
            f.write(data2)

    @staticmethod
    def record_changes() -> None:
        if RecordReplaySettings.record_replay.chosen == 0:
            return
        if not GameEvent.initialized:
            return
        data = bytearray()
        game_changes = []
        if Game.obj.now_playing_player_index != GameEvent.prev_now_plaing_player_id:
            game_changes.append(Game.obj.now_playing_player_index)
            GameEvent.prev_now_plaing_player_id = Game.obj.now_playing_player_index
        tile_changes = []
        for row in Game.obj.world.world:
             for tile in row:
                t = tile.serialize_updates()
                if t != SpecialTypes.NOTHING:
                    tile_changes.append(t)
        unit_changes = []
        for unit in Unit.units:
            u = unit.serialize_updates()
            if u != SpecialTypes.NOTHING:
                unit_changes.append(u)
        city_changes = []
        for city in City.cities:
            c = city.serialize_updates()
            if c != SpecialTypes.NOTHING:
                city_changes.append(c)
        player_changes = []
        for player in Player.players:
            flat_vision = [item for sublist in player.vision for item in sublist]
            player_changes.append((player.id, player.money, player.techs, list_bool_to_list_int32(flat_vision)))

        change_data = [game_changes, tile_changes, unit_changes, city_changes, player_changes]
        data = to_bytes(change_data)
        with open(RecordReplaySettings.replay_path / f"{RecordReplaySettings.replay_file_name}.replay", "ab") as f:
            f.write(data)


def list_bool_to_list_int32(x: list[bool]) -> list[int]:
    result = []
    for i in range(len(x) // 32 + (1 if len(x) % 32 else 0)):
        num = 0
        for j in range(32):
            if 32 * i + j >= len(x):
                break
            num += x[32 * i + j] * (2 **(31 - j))
        result.append(num)
    return result

def list_int32_to_list_bool(x: list[int]) -> list[bool]:
    result = []
    for num in reversed(x):
        for j in range(32):
            result.append(1 & num)
            num = num >> 1
    result.reverse()
    return result

