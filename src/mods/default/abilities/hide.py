from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Hide(Ability):
    name = "hide"

    @staticmethod
    def get_visibility(unit: Unit, pid: int):
        return pid == unit.owner
