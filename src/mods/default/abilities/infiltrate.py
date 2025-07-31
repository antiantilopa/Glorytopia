from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Infiltrate(Ability):
    name = "infiltrate"

    def infiltrate(city: City):
        pass
        # TODO: implement infiltrate ability

    @staticmethod
    def after_movement(unit):
        if World.object.cities_mask[unit.pos.y][unit.pos.x]:
            for city in City.cities:
                if city.pos == unit.pos:
                    if city.owner != unit.owner:
                        unit.health = 0
                        Infiltrate.infiltrate(city)
                        break
                    else:
                        break
    
    @staticmethod
    def after_attack(unit, other):
        if World.cities_mask[other.pos.y][other.pos.x]:
            for city in City.cities:
                if city.pos == unit.pos:
                    if city.owner != unit.owner:
                        unit.health = 0
                        Infiltrate.infiltrate(city)
                        break
                    else:
                        break
