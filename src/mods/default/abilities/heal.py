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

def heal(unit: Unit):
    if unit.moved or unit.attacked:
        return
    for dpos in adjacent:
        other = World.object.get_unit(unit.pos + dpos)
        if other is None:
            continue
        if other.owner != unit.owner:
            continue
        other.heal()
    unit.moved = True
    unit.attacked = True

class Heal(Ability):
    name = "heal"
    
    actions = {1269223: heal}
