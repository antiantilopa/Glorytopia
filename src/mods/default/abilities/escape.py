from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Escape(Ability):
    name = "escape"
    
    @staticmethod
    def after_attack(unit: Unit, _):
        unit.moved = False
