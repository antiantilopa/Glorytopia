from pathlib import Path

from netio.serialization.serializer import BaseReader, Serializable, SpecialTypes
from shared.asset_types import TechNode
from shared.city import CityData
from shared.globals.mod_versions import ModConfig
from shared.player import PlayerData_
from shared.tile import TileData
from shared.unit import UnitData
from shared.util.position import Pos

from engine_antiantilopa import Vector2d

from . import game_classes
from . import ui

b = BaseReader()

class GameData:
    world_size: Pos
    player_number: int
    now_playing_player_id: int

    def __init__(self, world_size: Pos, player_number: int, now_plaing_player_id: int):
        self.world_size = world_size
        self.player_number = player_number
        self.now_playing_player_id = now_plaing_player_id

    def __repr__(self):
        return f"GameData <{self.world_size}, {self.player_number}, {self.now_playing_player_id}>"

    def __str__(self):
        return f"GameData <{self.world_size}, {self.player_number}, {self.now_playing_player_id}>"

class Player:
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
    id: int
    money: int
    techs: list[TechNode]
    vision: list[int]

    def __init__(self, id: int, money: int, techs: list[TechNode], vision: list[int]):
        self.id = id
        self.money = money
        self.techs = techs
        self.vision = vision

    def get_main_color(self):
        return Player.colors[Replay.get_player_data_by_id(self.id).color][0]
    
    def get_secondary_color(self):
        return Player.colors[Replay.get_player_data_by_id(self.id).color][1]
    
    def get_vision(self) -> list[list[bool]]:
        flat = list_int32_to_list_bool(self.vision)
        width = Replay.game_data.world_size.intx()
        height = Replay.game_data.world_size.inty()
        assert len(flat) >= width * height, "Vision data is smaller than world size."
        vision = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(flat[y * width + x])
            vision.append(row)
        return vision
    
    def get_vision_at(self, pos: Pos) -> bool:
        flat = list_int32_to_list_bool(self.vision)
        return flat[pos.inty() * Replay.game_data.world_size.intx() + pos.intx()]

    def __repr__(self):
        return f"Player <{self.id}, {self.money}, {self.techs}, {self.vision}>"

    def __str__(self):
        return f"Player <{self.id}, {self.money}, {self.techs}, {self.vision}>"

class Replay:
    watch_as: int = 0
    game_data: GameData = None

    world: list[list[TileData]] = []

    tiles: list[game_classes.Tile] = []
    units: list[game_classes.Unit] = []
    cities: list[game_classes.City] = []
    players: list[Player] = []
    player_datas: list[PlayerData_] = []

    frame: int = 0

    frames_data: list[tuple] = []

    @staticmethod
    def init(mods: list[ModConfig], 
            game_data: GameData,
            player_datas: list[PlayerData_], 
            tiles: list[TileData], 
            units: list[UnitData], 
            cities: list[CityData], 
            players: list[Player]):
        # TODO check mods

        Replay.game_data = game_data
        Replay.tiles = [game_classes.Tile(tile) for tile in tiles]
        Replay.units = [game_classes.Unit(unit) for unit in units]
        Replay.cities = [game_classes.City(city) for city in cities]
        Replay.players = players
        Replay.player_datas = player_datas
        Replay.world = [[0] * game_data.world_size.x for _ in range(game_data.world_size.y)]
        for y in range(game_data.world_size.y):
            for x in range(game_data.world_size.x):
                for tile in tiles:
                    if tile.pos == Pos(x, y):
                        Replay.world[y][x] = tile
                        break
    
    @staticmethod
    def create_initial_objects():
        for tile in Replay.tiles:
            tile.on_create()
        for city in Replay.cities:
            city.on_create()
        for unit in Replay.units:
            unit.on_create()
        ui.update_money_label(Replay.get_player_by_id(Replay.watch_as).money)
        ui.update_now_playing_label(Replay.get_player_data_by_id(Replay.game_data.now_playing_player_id).nickname)
        game_classes.update_fog_of_war()

    @staticmethod
    def world_size_as_Vector2d() -> Vector2d:
        return Vector2d(Replay.game_data.world_size.x, Replay.game_data.world_size.y)

    @staticmethod
    def next_frame():
        if Replay.frame >= len(Replay.frames_data):
            return
        
        frame_data = Replay.frames_data[Replay.frame]
        Replay.frame += 1
        print(frame_data)
        game_changes, tile_changes, unit_changes, city_changes, player_changes = frame_data
        game_changes = Serializable.parse(game_changes, int)
        player_changes = Serializable.parse(player_changes, list[tuple[int, int, list[TechNode], list[int]]], 1)
        if game_changes != SpecialTypes.NOTHING:
            Replay.game_data.now_playing_player_id = game_changes
            ui.update_now_playing_label(Replay.get_player_data_by_id(Replay.game_data.now_playing_player_id).nickname)
        for tile_data in tile_changes:
            tile = Replay.get_tile_by_id(tile_data[1])
            tile.tdata.deserialize_updates(tile_data)
            tile.on_update()
        for unit_data in unit_changes:
            unit = Replay.get_unit(unit_data[1])
            if unit is None:
                new_unit = game_classes.Unit(UnitData.deserialize(unit_data, 1))
                new_unit.on_create()
                Replay.units.append(new_unit)
            else:
                unit.udata.deserialize_updates(unit_data)
                if unit.udata.health <= 0:
                    unit.on_destroy()
                    Replay.units.remove(unit)
                else:
                    unit.on_update()
        for city_data in city_changes:
            city = Replay.get_city(city_data[1])
            city.cdata.deserialize_updates(city_data)
            city.on_update()
        for player in player_changes:
            p = Replay.get_player_by_id(player[0])
            p.money = player[1]
            p.techs = player[2]
            p.vision = player[3] # TODO!
            ui.update_money_label(Replay.get_player_by_id(Replay.watch_as).money)
            game_classes.update_fog_of_war()

    @staticmethod
    def get_tile_data(pos: Pos) -> TileData | None:
        return Replay.world[pos.inty()][pos.intx()]
    
    @staticmethod
    def get_tile(pos: Pos) -> "game_classes.Tile":
        for tile in Replay.tiles:
            if tile.tdata.pos == pos:
                return tile
        return None
    
    @staticmethod
    def get_tile_by_id(id: int) -> "game_classes.Tile":
        for tile in Replay.tiles:
            if tile.tdata._id == id:
                return tile
        return None
    
    @staticmethod
    def get_city(id: int) -> "game_classes.City":
        for city in Replay.cities:
            if city.cdata._id == id:
                return city
        return None
    
    @staticmethod
    def get_unit(id: int) -> "game_classes.Unit|None":
        for unit in Replay.units:
            if unit.udata._id == id:
                return unit
        return None

    @staticmethod
    def get_player_by_id(id: int) -> Player:
        for player in Replay.players:
            if player.id == id:
                return player
        raise KeyError(f"Player with id {id} not found in replay players.")
    
    @staticmethod
    def get_player_data_by_id(id: int) -> PlayerData_:
        for player in Replay.player_datas:
            if player.id == id:
                return player
        raise KeyError(f"Player with id {id} not found in replay players.")

def load(path: Path):
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
    game_data = GameData(*Serializable.parse(initial_data[1], tuple[Pos, int, int], 1))
    player_datas = Serializable.parse(initial_data[2], list[PlayerData_], 1)
    tiles = Serializable.parse(initial_data[3], list[TileData], 1)
    units = Serializable.parse(initial_data[4], list[UnitData], 1) 
    cities = Serializable.parse(initial_data[5], list[CityData], 1)
    players = [Player(*Serializable.parse(i, tuple[int, int, list[TechNode], list[int]], 1)) for i in initial_data[6]]

    Replay.init(mods, game_data, player_datas, tiles, units, cities, players)
    Replay.frames_data = frames

def list_int32_to_list_bool(x: list[int]) -> list[bool]:
    result = []
    for num in reversed(x):
        for j in range(32):
            result.append(1 & num)
            num = num >> 1
    result.reverse()
    return result