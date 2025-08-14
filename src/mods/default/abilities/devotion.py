from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Devotion(Ability):
    name = "devotion"
    
    @staticmethod
    def additional_defense(unit: Unit, other: Unit) -> int:
        print("devotion additional attack was used")
        if World.object.get(unit.pos).owner == unit.owner:
            return 1
        return 0

    @staticmethod
    def additional_attack(unit: Unit, other: Unit) -> int:
        print("devotion additional defense was used")
        if World.object.get(other.pos).owner == unit.owner:
            return 1
        return 0