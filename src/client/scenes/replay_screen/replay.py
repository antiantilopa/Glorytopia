from pathlib import Path

from netio.datatypes import PlayerData
from shared.asset_types import TechNode
from shared.city import CityData
from shared.globals.mod_versions import ModConfig
from shared.tile import TileData
from shared.unit import UnitData
from shared.util.position import Pos

class GameData:
    world_size: Pos
    player_number: int
    now_playing_player_id: int

class Player:
    id: int
    money: int
    techs: list[TechNode]
    vision: list[list[bool]]

class Replay:

    game_data: GameData = None

    tiles: list[TileData] = []
    units: list[UnitData] = []
    cities: list[CityData] = []
    players: list[PlayerData] = []

    frame: int = 0

    frames_data: list[tuple] = []

    @staticmethod
    def init(mods: list[ModConfig], 
            game_data: GameData,
            player_datas: list[PlayerData], 
            tiles: list[TileData], 
            units: list[UnitData], 
            cities: list[CityData], 
            players: list[tuple[int, int, list[TechNode], list[int]]]):
        pass

def load(path: Path):
    with open(path, "rb") as f:
        data = f.read()

