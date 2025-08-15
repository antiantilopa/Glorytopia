from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Surprise(Ability):
    name = "surprise"

    @staticmethod
    def retaliation_mitigate(*_):
        return 0
