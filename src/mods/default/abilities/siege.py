from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Siege(Ability):
    name = "siege"
    
    @staticmethod
    def additional_attack(unit: Unit, other: Unit) -> int:
        if World.object.cities_mask[other.pos.y][other.pos.y] == 0:
            return 0
        for city in City.cities:
            if city.pos == other.pos:
                if city.owner == unit.owner:
                    return 0
                break
        return 2