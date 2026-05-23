from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.util.position import Pos

adjacent = [
    Pos(-1, -1),
    Pos(-1, 0),
    Pos(-1, 1),
    Pos(0, -1),
    Pos(0, 1),
    Pos(1, -1),
    Pos(1, 0),
    Pos(1, 1),
]

class Splash(Ability):
    name = "splash"
    
    @staticmethod
    def after_attack(unit: Unit, other: Unit):
        for d in adjacent:
            adj_unit = World.object.get_unit(other.pos + d)
            if adj_unit is None:
                continue
            if adj_unit.owner == unit.owner:
                continue
            attack, _ = unit.calc_attack(adj_unit)
            attack = attack // 2
            other.recv_damage(attack)