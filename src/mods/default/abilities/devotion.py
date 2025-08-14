from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Devotion(Ability):
    name = "devotion"
    
    @staticmethod
    def retaliation_bonus(unit: Unit, defense_result: int) -> int:
        return defense_result