import os
from server.globals.backup import BackupSettings
from shared.asset_types import Nation, TileType, ResourceType, UnitType
from shared.city import CityData
from shared.util.position import Pos, Angle
from math import pi
from random import random, randint
from pathlib import Path

from .world import World
from .player import Player
from .city import City
from .unit import Unit

def abs(x):
    return x * ((x > 0) * 2 - 1)

class Game:
    now_playing_player_index: int
    players: list[Player]
    world: World
    turn_number: int
    obj: "Game" = None

    def __init__(self, size: Pos, player_number: int, start_new_game: bool = True) -> None:
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
            
            self.turn_number = 0
        else:
            if World.object is None:
                self.world = World(size.x, size.y, empty=True)
            else:
                self.world = World.object
            if len(Player.players) == 0:
                self.players = [Player() for i in range(player_number)]
            else:
                self.players = Player.players
    
    def start(self):
        self.players[self.now_playing_player_index].start_turn()

    def update_world_masks(self):
        self.world.cities_mask = [[0] * self.world.size.x for _ in range(self.world.size.y)]
        self.world.unit_mask = [[0] * self.world.size.x for _ in range(self.world.size.y)]
        for city in City.cities:
            self.world.cities_mask[city.pos.y][city.pos.x] = 1
        for unit in Unit.units:
            self.world.unit_mask[unit.pos.y][unit.pos.x] = 1

    def place_random_city(self):
        # another algorithm would be better. For example, we could:
        # have a map of possible places, and shuffle around them, then discard those that are too close. boom, and every possible city place is used.
        for _ in range(500): 
            x = randint(1, World.object.size.x - 2)
            y = randint(1, World.object.size.y - 2)
            if not World.object.get(Pos(x, y)).type.is_water:
                is_far_enough = True
                for c in City.cities:
                    if max(abs(c.pos.x - x), abs(c.pos.y - y)) < 3:
                        is_far_enough = False
                        break
                if is_far_enough:
                    World.object.get(Pos(x, y)).type = TileType.get("plain")
                    City(Pos(x, y), -1)
                    World.object.cities_mask[y][x] = 1
                    return

    def place_resources(self):
        def distance_to_nearest(pos: Pos) -> int:
            for distance in range(World.object.size.x):
                for i in range(2 * distance + 1):
                    for j in range(2 * distance + 1):
                        if World.object.is_in(Pos(i - distance, j - distance) + pos):
                            if World.object.cities_mask[pos.y + j - distance][pos.x + i - distance] == 1:
                                return distance
            return -1

        for i in range(World.object.size.x):
            for j in range(World.object.size.y):
                dist = distance_to_nearest(Pos(i, j))
                if dist == 0:
                    continue 
                chance_sum = 1 # 1 for no resource
                for resource in ResourceType.values():
                    if World.object.get(Pos(i, j)).type in resource.ttypes:
                        chance_sum += resource.spawn_rates.get(dist, 0)
                rand = random() * chance_sum
                if rand < 1:
                    continue 
                rand -= 1
                for resource in ResourceType.values():
                    if World.object.get(Pos(i, j)).type in resource.ttypes:
                        rand -= resource.spawn_rates.get(dist, 0)
                        if rand <= 0:
                            World.object.get(Pos(i, j)).resource = resource
                            break
                    
    def place_players(self):
        distance_to_center_of_map = World.object.size.x * 3 / 10

        random_angle = random() * 2 * pi
        for player in self.players:
            angle = Angle(2 * pi * player.id / len(self.players) + random_angle)

            place = angle.to_Pos() * distance_to_center_of_map + World.object.size / 2

            place.x = round(place.x)
            place.y = round(place.y)
            World.object.get(place).type = TileType.get("plain")
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

        self.players[self.now_playing_player_index].end_turn()

        prev = self.now_playing_player_index
        self.now_playing_player_index += 1
        self.now_playing_player_index %= len(self.players)
        while len(self.players[self.now_playing_player_index].cities) + len(self.players[self.now_playing_player_index].units) == 0:
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