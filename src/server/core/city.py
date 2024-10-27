from random_names import random_funny_name as random_name
from shared.vmath import Vector2d
from shared.unit_types import UnitType
from shared.city import CityData

from .world import World
from ..unit import Unit


class City(CityData):
    cities: list["City"] = []

    def __init__(self, pos: Vector2d, owner: int):
        CityData.__init__(self, pos, owner, random_name(), 1, 0, 0, False, False, [pos])
        City.cities.append(self)

    def init_domain(self, world: World):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if world.is_in(self.pos + Vector2d(dx, dy)):
                    if world.get(self.pos + Vector2d(dx, dy)).owner == -1:
                        self.domain.append(self.pos + Vector2d(dx, dy))
                        world.get(self.pos + Vector2d(dx, dy)).owner = self.owner

    def grow_population(self, count):
        self.population += count

    def create_unit(self, utype: UnitType):
        unit = Unit(utype, self.owner, self.pos)
    