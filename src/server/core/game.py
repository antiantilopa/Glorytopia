import os
from shared.city import SerializedCity
from shared.unit import SerializedUnit
from server.globals.backup import BackupSettings
from .world import World, SerializedWorld
from .player import Player, SerializedPlayer
from .city import City
from .unit import Unit
from shared.asset_types import TileType, ResourceType, UnitType
from engine_antiantilopa import Vector2d, Angle
from math import pi
from random import random, randint
from .updating_object import UpdatingObject
from serializator.net import Serializator
from pathlib import Path
def abs(x):
    return x * ((x > 0) * 2 - 1)

SerializedGame = tuple[list[SerializedPlayer], SerializedWorld, list[SerializedCity], list[SerializedUnit], int, int]

class Game:
    now_playing_player_index: int
    players: list[Player]
    world: World
    turn_number: int
    obj: "Game" = None

    def __init__(self, size: Vector2d, player_number: int, start_new_game: bool = True) -> None:
        Game.obj = self
        if start_new_game:
            self.world = World(size.x, size.y)
            self.now_playing_player_index = 0
            self.players = [Player() for i in range(player_number)]
            self.place_players()
            for _ in range(((size.x - 2) * (size.y - 2)) // 16):
                self.place_random_city()
            self.place_resources()
            for player in self.players:
                unit = player.cities[0].create_unit(UnitType.get("warrior"))
                player.units.append(unit)
                player.update_vision()

            for unit in Unit.units:
                unit.refresh()
            
            for obj in UpdatingObject.objs:
                obj.refresh_updated()
            
            self.turn_number = 0
            UpdatingObject.updated_objs.clear()
            self.players[0].start_turn()
        else:
            if World.object is None:
                self.world = World(size.x, size.y, empty=True)
            else:
                self.world = World.object
            if len(Player.players) == 0:
                self.players = [Player() for i in range(player_number)]
            else:
                self.players = Player.players
    
    def place_random_city(self):
        # another algorithm would be better. For example, we could:
        # have a map of possible places, and shuffle around them, then discard those that are too close. boom, and every possible city place is used.
        for _ in range(500): 
            x = randint(1, World.object.size.x - 2)
            y = randint(1, World.object.size.y - 2)
            if not World.object.get(Vector2d(x, y)).ttype.is_water:
                is_far_enough = True
                for c in City.cities:
                    if max(abs(c.pos.x - x), abs(c.pos.y - y)) < 3:
                        is_far_enough = False
                        break
                if is_far_enough:
                    World.object.get(Vector2d(x, y)).ttype = TileType.get("plain")
                    City(Vector2d(x, y), -1)
                    World.object.cities_mask[y][x] = 1
                    return

    def place_resources(self):

        def distance_to_nearest(pos: Vector2d) -> int:
            for distance in range(World.object.size.x):
                for i in range(2 * distance + 1):
                    for j in range(2 * distance + 1):
                        if World.object.is_in(Vector2d(i - distance, j - distance) + pos):
                            if World.object.cities_mask[pos.y + j - distance][pos.x + i - distance] == 1:
                                return distance
            return -1

        for i in range(World.object.size.x):
            for j in range(World.object.size.y):
                dist = distance_to_nearest(Vector2d(i, j))
                if dist == 0:
                    continue 
                chance_sum = 1 # 1 for no resource
                for resource in ResourceType.values():
                    if World.object.get(Vector2d(i, j)).ttype in resource.ttypes:
                        chance_sum += resource.spawn_rates.get(dist, 0)
                rand = random() * chance_sum
                if rand < 1:
                    continue 
                rand -= 1
                for resource in ResourceType.values():
                    if World.object.get(Vector2d(i, j)).ttype in resource.ttypes:
                        rand -= resource.spawn_rates.get(dist, 0)
                        if rand <= 0:
                            World.object.get(Vector2d(i, j)).resource = resource
                            break
                    
    def place_players(self):
        distance_to_center_of_map = World.object.size.x * 3 / 10

        random_angle = random() * 2 * pi
        for player in self.players:
            angle = Angle(2 * pi * player.id / len(self.players) + random_angle)

            place = angle.to_vector2d() * distance_to_center_of_map + World.object.size / 2

            place.x = round(place.x)
            place.y = round(place.y)
            World.object.get(place).ttype = TileType.get("plain")
            city = City(place, player.id)
            World.object.cities_mask[place.y][place.x] = 1
            player.cities.append(city)
            city.init_domain()
            city.is_capital = True
            continue
    
    def remove_dead_units(self):
        i = 0
        while i < len(Unit.units):
            unit = Unit.units[i]
            if unit.health <= 0:
                unit.destroy()
                i -= 1
            i += 1
    
    def next_player_turn(self):
        
        if BackupSettings.backup_number.value > 0:
            self.save(f"{BackupSettings.save_folder_name}", f"turn{self.turn_number}-{self.now_playing_player_index}.save")

        self.players[self.now_playing_player_index].end_turn()

        prev = self.now_playing_player_index
        self.now_playing_player_index += 1
        self.now_playing_player_index %= len(self.players)
        while len(self.players[self.now_playing_player_index].cities) + len(self.players[self.now_playing_player_index].cities) == 0:
            if self.players[self.now_playing_player_index].is_dead == True:
                self.now_playing_player_index += 1
                self.now_playing_player_index %= len(self.players)
            else:
                for i in range((World.object.size.x)):
                    for j in range((World.object.size.y)):
                        self.players[self.now_playing_player_index].vision[j][i] = 1
                self.now_playing_player_index += 1
                self.now_playing_player_index %= len(self.players)

        if prev >= self.now_playing_player_index:
            self.turn_number += 1

        self.players[self.now_playing_player_index].start_turn()

    def save(self, folder_name: str = "", name: str = "glorytopia.save"):
        if BackupSettings.backup_number.value == 0:
            return
        if BackupSettings.backup_number.value != -1:
            while len(os.listdir(Path("../saves/") / folder_name)) >= BackupSettings.backup_number.value:
                saves = os.listdir(Path("../saves/") / folder_name)
                saves.sort(key=lambda x: os.path.getmtime(Path("../saves/") / folder_name / x))
                os.remove(Path("../saves/") / folder_name / saves[0])
        with open(Path("../saves/") / folder_name / name, "wb") as f:
            f.write(Serializator.encode(self.to_serializable()))
        

    def to_serializable(self) -> SerializedGame:
        return [
            [player.to_serializable() for player in self.players],
            World.object.to_serializable(),
            [city.to_serializable() for city in City.cities],
            [unit.to_serializable() for unit in Unit.units],
            self.now_playing_player_index,
            self.turn_number
        ]

    @staticmethod
    def from_serializable(serializable: SerializedGame) -> "Game":
        world = World.from_serializable(serializable[1])
        cities = [City.from_serializable(city) for city in serializable[2]]
        units = [Unit.from_serializable(unit) for unit in serializable[3]]
        players = [Player.from_serializable(player) for player in serializable[0]]
        
        game = Game(world.size, len(players), start_new_game=False)
        game.now_playing_player_index = serializable[4]
        game.turn_number = serializable[5]
        game.players = players
        game.players.sort(key=lambda p: p.id)
        game.world = world
        City.cities = cities
        Unit.units = units
        
        for player in game.players:
            player.update_vision()
        
        while 0 < len(UpdatingObject.updated_objs):
            UpdatingObject.updated_objs[0].refresh_updated()
        return game

    @staticmethod
    def clear_game() -> None:
        while len(Unit.units) != 0:
            Unit.units[0].destroy()
        while len(City.cities) != 0:
            City.cities[0].destroy()
        World.object.get(Vector2d(0, 0)).destroy()
        World.object.world = [[]]
        World.object = None
        while len(Player.players) != 0:
            Player.players[0].destroy()
        Player.ID = 0
        Game.obj.players = []
        Game.obj.world = None
        World.object = None
        Game.obj = None