from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Siege(Ability):
    name = "siege"
    
    @staticmethod
    def additional_attack(unit: Unit, other: Unit) -> int:
        if World.object.get_city(other.pos) is None:
            return 0
        city = World.object.get_city(other.pos)
        if city.owner == unit.owner:
            return 0
        return 2