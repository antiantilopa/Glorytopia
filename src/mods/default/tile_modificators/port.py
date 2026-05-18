from shared.asset_types import BuildingType, UnitType
from shared.effect import Effect, EffectType
from shared.modificator import TileModificator, TileModificatorType
from shared.tile import TileData

class Port(TileModificatorType):
    name = "port"

    @staticmethod
    def ignore_water(modificator, unit, tile):
        return 1
    
    @staticmethod
    def stop_movement(modificator, unit, tile):
        if not unit.type.water:
            return 1
        
    @staticmethod
    def ignore_stop_movement(modificator, unit, tile):
        return -1
    
    @staticmethod
    def on_unit_enter(modificator, tile, unit):
        unit.effects.append(Effect(EffectType.get("embarked"), -1, [unit.type.id]))
        unit.type = UnitType.get("raft")