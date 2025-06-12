from .world import World
from .player import Player
from .city import City
from .unit import Unit
from shared.tile_types import TileTypes, ResourceTypes
from shared.unit_types import UnitTypes
from engine_antiantilopa import Vector2d, Angle
from math import pi
from random import randint


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
            player.create_unit(player.cities[0].pos, UnitTypes.warrior)
            player.money += 2
            player.update_vision()

        for unit in Unit.units:
            unit.refresh()
    
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
                    World.object.get(Vector2d(x, y)).ttype = TileTypes.plain
                    City(Vector2d(x, y), -1)
                    World.object.cities_mask[y][x] = 1
                    return

    def place_resources(self):

        def is_city_nearby(pos: Vector2d, distance: int):
            for i in range(2 * distance + 1):
                for j in range(2 * distance + 1):
                    if World.object.is_in(Vector2d(i - distance, j - distance) + pos):
                        if World.object.cities_mask[pos.y + j - distance][pos.x + i - distance] == 1:
                            return True
            return False


        for i in range(World.object.size.x):
            for j in range(World.object.size.y):
                if is_city_nearby(Vector2d(i, j), 0):
                    continue
                if is_city_nearby(Vector2d(i, j), 2):
                    if World.object.get(Vector2d(i, j)).ttype.is_water:
                        rand = randint(0, 1)
                        if rand == 1:
                            World.object.get(Vector2d(i, j)).resource = ResourceTypes.fish
                    elif World.object.get(Vector2d(i, j)).ttype == TileTypes.plain:
                        rand = randint(1, 48)
                        if is_city_nearby(Vector2d(i, j), 1):
                            if rand < 19:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.fruits
                            elif rand < 37:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.crops
                        else:
                            if rand < 7:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.fruits
                            elif rand < 13:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.crops
                    elif World.object.get(Vector2d(i, j)).ttype == TileTypes.forest:
                        rand = randint(1, 38)
                        if is_city_nearby(Vector2d(i, j), 1):
                            if rand < 20:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.wild_animals
                        else:
                            if rand < 6:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.wild_animals
                    elif World.object.get(Vector2d(i, j)).ttype == TileTypes.mountain:
                        rand = randint(1, 14)
                        if is_city_nearby(Vector2d(i, j), 1):
                            if rand < 12:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.metal
                        else:
                            if rand < 4:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.metal

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
                World.object.get(place).ttype = TileTypes.plain
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
                self.players[unit.owner].units.remove(unit)
                World.object.unit_mask[unit.pos.inty()][unit.pos.intx()] = 0
                for other in Unit.units:
                    if other.pos == unit.pos:
                        World.object.unit_mask[unit.pos.inty()][unit.pos.intx()] = 1
                        break
                Unit.units.remove(unit)
                if unit.attached_city is not None and unit.attached_city.owner == unit.owner:
                    unit.attached_city.fullness -= 1
                i -= 1
                del unit
            i += 1
    