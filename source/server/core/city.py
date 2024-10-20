from tile import Tile, World
from unit import Unit
from random_names import random_funny_name as random_name
from shared.vmath import Vector2d
from shared.tile_types import TileTypes
from shared.unit_types import UnitType

class City:
    name: str
    level: int
    population: int
    fullness: int
    forge: bool
    walls: bool
    domain: list[Tile]
    pos: Vector2d

    def __init__(self, pos: Vector2d, owner):
        self.pos = pos
        self.owner = owner
        self.name = random_name()
        self.level = 0
        self.population = 0
        self.fullness = 0
        self.forge = 0
        self.walls = 0
        self.domain = [self]

    def init_domain(self, world: World):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if world.isIn(self.tile.pos + Vector2d(dx, dy)):
                    if world.get(self.tile.pos + Vector2d(dx, dy)).owner == -1:
                        self.domain.append(world.get(self.tile.pos + Vector2d(dx, dy)))
                        world.get(self.tile.pos + Vector2d(dx, dy)).owner = self.owner

    def grow_population(self, count):
        self.population += count

    def create_unit(self, utype: UnitType):
        unit = Unit(utype, self.owner, self.pos)
    