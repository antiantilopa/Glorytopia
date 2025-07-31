from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Dash(Ability):
    name = "dash"

    @staticmethod
    def after_movement(unit: Unit):
        unit.attacked = False
