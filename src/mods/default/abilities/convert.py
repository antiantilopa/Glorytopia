from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Convert(Ability):
    name = "convert"

    @staticmethod
    def after_attack(unit, other):

        if other.attached_city is not None and other.attached_city.owner == other.owner:
            other.attached_city.fullness -= 1
        other.attached_city = None
        other.owner = unit.owner
        other.attacked = True
        other.moved = True
    
    @staticmethod
    def retaliation_mitigate(unit, defense_result):
        return 0