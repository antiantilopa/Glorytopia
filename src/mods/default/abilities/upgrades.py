from server.core.ability import Ability
from server.core.player import Player
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.asset_types import TileType, UnitType



def upgrade_to_boat(unit: Unit):
    player = Player.by_id(unit.owner)
    new_type = UnitType.get("boat")
    if World.object.get(unit.pos).owner != unit.owner:
        return
    if player.money <= new_type.cost:
        return
    for tech in player.techs:
        if new_type in tech.units:
            break
    else:
        return
    unit.type = new_type

def upgrade_to_galley(unit: Unit):
    player = Player.by_id(unit.owner)
    new_type = UnitType.get("galley")
    if World.object.get(unit.pos).owner != unit.owner:
        return
    if player.money <= new_type.cost:
        return
    for tech in player.techs:
        if new_type in tech.units:
            break
    else:
        return
    unit.type = new_type

def upgrade_to_bomber(unit: Unit):
    player = Player.by_id(unit.owner)
    new_type = UnitType.get("bomber")
    if World.object.get(unit.pos).owner != unit.owner:
        return
    if player.money <= new_type.cost:
        return
    for tech in player.techs:
        if new_type in tech.units:
            break
    else:
        return
    unit.type = new_type

class Upgrades(Ability):
    name = "upgrades"

    actions = {
        596349512: upgrade_to_boat,
        596349513: upgrade_to_galley,
        596349514: upgrade_to_bomber,
    }