from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Scout(Ability):
    name = "scout"

    @staticmethod
    def get_vision_range(unit):
        return 2
