from pathlib import Path

from netio.serialization.serializer import BaseReader, Serializable
from server.core.city import City
from server.core.game import Game
from server.core.player import Player
from server.core.tile import Tile
from server.core.unit import Unit
from shared.asset_types import TechNode
from shared.player import PlayerData_
from shared.globals.mod_versions import ModConfig
from shared.util.position import Pos

b = BaseReader()

class Player_dummy:
    id: int
    money: int
    techs: list[TechNode]
    vision: list[int]

    def __init__(self, id: int, money: int, techs: list[TechNode], vision: list[int]):
        self.id = id
        self.money = money
        self.techs = techs
        self.vision = vision

class GameData:
    world_size: Pos
    player_number: int
    now_playing_player_id: int
    turn_number: int

    def __init__(self, world_size: Pos, player_number: int, now_plaing_player_id: int, turn_number: int = 0):
        self.world_size = world_size
        self.player_number = player_number
        self.now_playing_player_id = now_plaing_player_id
        self.turn_number = turn_number

def load(path: Path) -> list[PlayerData_]:
    with open(path, "rb") as f:
        data = f.read()

    frames = []
    
    initial_data, start = b._bytes_to_serialized(data)
    start += 1

    while start < len(data):
        frame, lenght = b._bytes_to_serialized(data, start)
        start += lenght + 1
        frames.append(frame)

    mods = Serializable.parse(initial_data[0], list[ModConfig], 1)

    game_data = GameData(*Serializable.parse(initial_data[1], tuple[Pos, int, int, int], 1))
    Game(game_data.world_size, game_data.player_number, 0)
    Game.obj.now_playing_player_index = game_data.now_playing_player_id
    Game.obj.turn_number = game_data.turn_number

    player_datas = Serializable.parse(initial_data[2], list[PlayerData_], 1)
    players = [Player_dummy(*Serializable.parse(i, tuple[int, int, list[TechNode], list[int]], 1)) for i in initial_data[6]]
    for player_dummy in players:
        player = Player.by_id(player_dummy.id)
        player.money = player_dummy.money
        player.techs = player_dummy.techs
        player.vision = get_vision(player_dummy.vision, game_data.world_size)

    tiles = Serializable.parse(initial_data[3], list[Tile], 1, 1)
    Game.obj.world.update(tiles)

    cities = Serializable.parse(initial_data[5], list[City], 1)
    City.cities = cities

    units = Serializable.parse(initial_data[4], list[Unit], 1)
    Unit.units = units

    for unit in units:
        if unit.owner != -1:
            Player.by_id(unit.owner).units.append(unit)
        unit.update_attached_city()
        unit.init()

    for city in cities:
        if city.owner != -1:
            Player.by_id(city.owner).cities.append(city)
        city.init()

    for unit in units:
        unit.update_attached_city_id()

    Game.obj.update_world_masks()

    return player_datas

def list_int32_to_list_bool(x: list[int]) -> list[bool]:
    result = []
    for num in reversed(x):
        for j in range(32):
            result.append(1 & num)
            num = num >> 1
    result.reverse()
    return result

def get_vision(vision: list[int], world_size: Pos) -> list[list[bool]]:
    flat = list_int32_to_list_bool(vision)
    width = world_size.intx()
    height = world_size.inty()
    assert len(flat) >= width * height, "Vision data is smaller than world size."
    vision = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(flat[y * width + x])
        vision.append(row)
    return vision