from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile

class Persist(Ability):
    name = "persist"

    @staticmethod
    def after_kill(unit, other):
        unit.attacked = False
