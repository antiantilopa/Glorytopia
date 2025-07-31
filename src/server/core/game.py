from .world import World
from .player import Player
from .city import City
from .unit import Unit
from shared.asset_types import TileType, ResourceType, UnitType
from engine_antiantilopa import Vector2d, Angle
from math import pi
from random import random, randint
from .updating_object import UpdatingObject


def abs(x):
    return x * ((x > 0) * 2 - 1)

class Game:
    players: list[Player]
    world: World

    def __init__(self, size: Vector2d, player_number: int):
        self.world = World(size.x, size.y)
        self.players = [Player() for i in range(player_number)]
        for _ in range(((size.x - 2) * (size.y - 2)) // 16):
            self.place_random_city()
        self.place_players()
        self.place_resources()
        for player in self.players:
            player.create_unit(player.cities[0].pos, UnitType.get("warrior"))
            player.money += 2
            player.update_vision()

        for unit in Unit.units:
            unit.refresh()
        
        for obj in UpdatingObject.objs:
            obj.refresh_updated()
        
        self.players[0].start_turn()
    
    def place_random_city(self):
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
                print(dist)
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

        def get_city_nearby_pos(pos: Vector2d, distance: int) -> Vector2d|None:
            for i in range(2 * distance + 1):
                for j in range(2 * distance + 1):
                    if i == distance and j == distance:
                        continue
                    if World.object.is_in(Vector2d(i - distance, j - distance) + pos):
                        if World.object.cities_mask[pos.y + j - distance][pos.x + i - distance] == 1:
                            return Vector2d(pos.x + i - distance, pos.y + j - distance)
            return None

        for player in self.players:
            angle = Angle(2 * pi * player.id / len(self.players))

            place = angle.to_vector2d() * distance_to_center_of_map + World.object.size / 2

            place.x = round(place.x)
            place.y = round(place.y)
            if World.object.cities_mask[place.y][place.x]:
                city_pos = place
                for city in City.cities:
                    if city.pos == city_pos:
                        break
                city.owner = player.id
                player.cities.append(city)
                city.init_domain()
                city.is_capital = True
                continue
            city_pos = get_city_nearby_pos(place, 1)
            if city_pos is not None:
                for city in City.cities:
                    if city.pos == city_pos:
                        break
                city.owner = player.id
                player.cities.append(city)
                city.init_domain()
                city.is_capital = True
                continue
            city_pos = get_city_nearby_pos(place, 2)
            if city_pos is not None:
                for city in City.cities:
                    if city.pos == city_pos:
                        break
                city.owner = player.id
                player.cities.append(city)
                city.init_domain()
                city.is_capital = True
                continue
            else:
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
    