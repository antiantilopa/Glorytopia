import os
from server.bot.bot import Bot
from server.core.tile import Tile
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
    players: list[Player|Bot]
    world: World
    turn_number: int
    obj: "Game" = None

    def __init__(self, size: Pos, player_number: int, bot_number: int, start_new_game: bool = True) -> None:
        Game.obj = self
        if start_new_game:
            self.world = World(size.x, size.y)
            self.now_playing_player_index = 0
            self.players = [Player() for i in range(player_number)]
            bots = [Bot(f"bot_{i}")  for i in range(bot_number)]
            for bot in bots:
                bot.memory.world = World.object
            self.players += bots
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
            self.players += [Bot(f"bot_{i}")  for i in range(bot_number)]
    
    def start(self):
        for tiles in self.world:
            for tile in tiles:
                for tile_mod in tile.modificators:
                    tile_mod.tmtype.on_start_turn(tile_mod.tmtype, tile, self.now_playing_player_index)
        self.players[self.now_playing_player_index].start_turn()

    def update_world_masks(self):
        self.world.city_mask = [[None] * self.world.size.x for _ in range(self.world.size.y)]
        self.world.unit_mask = [[None] * self.world.size.x for _ in range(self.world.size.y)]
        for city in City.cities:
            self.world.city_mask[city.pos.y][city.pos.x] = city
        for unit in Unit.units:
            self.world.unit_mask[unit.pos.y][unit.pos.x] = unit

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
                    new_city = City(Pos(x, y), -1)
                    World.object.city_mask[y][x] = new_city
                    return

    def place_resources(self):
        def distance_to_nearest(pos: Pos) -> int:
            for distance in range(World.object.size.x):
                for i in range(2 * distance + 1):
                    for j in range(2 * distance + 1):
                        if World.object.is_in(Pos(i - distance, j - distance) + pos):
                            if World.object.city_mask[pos.y + j - distance][pos.x + i - distance] is not None:
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
            World.object.city_mask[place.y][place.x] = city
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
    
    def end_turn(self):
        for tiles in self.world:
            for tile in tiles:
                for tile_mod in tile.modificators:
                    tile_mod.tmtype.on_end_turn(tile_mod.tmtype, tile, self.now_playing_player_index)
        self.players[self.now_playing_player_index].end_turn()

    def set_next_player_turn(self):
        prev = self.now_playing_player_index

        self.now_playing_player_index += 1
        self.now_playing_player_index %= len(self.players)

        while self.players[self.now_playing_player_index].calc_is_dead():
            self.now_playing_player_index += 1
            self.now_playing_player_index %= len(self.players)

        if prev >= self.now_playing_player_index:
            self.turn_number += 1

    def start_turn(self):
        for tiles in self.world:
            for tile in tiles:
                for tile_mod in tile.modificators:
                    tile_mod.tmtype.on_start_turn(tile_mod.tmtype, tile, self.now_playing_player_index)
        self.players[self.now_playing_player_index].start_turn()
        if isinstance(self.players[self.now_playing_player_index], Bot):
            bot = self.players[self.now_playing_player_index]
            stops = False
            while not stops:
                stops = bot.execute_moves(bot.get_moves(), bot.pdata)
            self.end_turn()
            self.set_next_player_turn()
            self.start_turn()