from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Stiff(Ability):
    name = "stiff"

    @staticmethod
    def retaliation_bonus(*_):
        return 0
