from server.core.world import World
from shared.asset_types import UnitType
from shared.effect import EffectType, Effect
from server.core.unit import Unit

class Embarked(EffectType):
    name = "embarked"
    stackable = False
    
    @staticmethod
    def after_movement(effect, unit):
        if effect.duration == 0:
            return
        if World.object.get(unit.pos).type.is_water:
            return
        utype = UnitType.by_id(effect.args[0])
        unit.type = utype
        effect.duration = 0

    @staticmethod
    def after_attack(effect, unit, other):
        if effect.duration == 0:
            return
        if World.object.get(unit.pos).type.is_water:
            return
        utype = UnitType.by_id(effect.args[0])
        unit.type = utype
        effect.duration = 0

    @staticmethod
    def after_kill(effect, unit, other):
        if effect.duration == 0:
            return
        if World.object.get(unit.pos).type.is_water:
            return
        utype = UnitType.by_id(effect.args[0])
        unit.type = utype
        effect.duration = 0

    @staticmethod
    def ignore_water(effect, unit, tile):
        if effect.duration == 0:
            return
        return 1
    
    @staticmethod
    def stop_movement(effect, unit, tile):
        if effect.duration == 0:
            return
        if not tile.type.is_water:
            return True
        return False