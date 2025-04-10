from .world import World
from .player import Player
from .city import City
from .unit import Unit
from shared.tile_types import TileTypes, ResourceTypes
from pygame_tools_tafh import Vector2d
from random import randint


def abs(x):
    return x * ((x > 0) * 2 - 1)

class Game:
    players: list[Player]

    def __init__(self, size: Vector2d, player_number: int):
        World(size.x, size.y)
        self.players = [Player() for i in range(player_number)]
        for _ in range(((size.x - 2) * (size.y - 2)) // 16):
            self.place_random_city()
        self.place_resources()

    
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
                    if i == distance and j == distance:
                        continue
                    if World.object.is_in(Vector2d(i - distance, j - distance) + pos):
                        if World.object.cities_mask[pos.y + j - distance][pos.x + i - distance] == 1:
                            return True
            return False


        for i in range(World.object.size.x):
            for j in range(World.object.size.y):
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
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.fruits
                    elif World.object.get(Vector2d(i, j)).ttype == TileTypes.mountain:
                        rand = randint(1, 14)
                        if is_city_nearby(Vector2d(i, j), 1):
                            if rand < 12:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.metal
                        else:
                            if rand < 4:
                                World.object.get(Vector2d(i, j)).resource = ResourceTypes.metal