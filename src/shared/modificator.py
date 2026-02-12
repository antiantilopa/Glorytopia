from netio import Serializable, GenericType, SerializeField
from shared.asset_types import BuildingType, TerraForm
from shared.generic_object import GenericObject
from . import tile as Tile
from . import unit as Unit

class TileModificatorType(GenericType):
    
    @staticmethod
    def on_yaderka_boom(modificator: "TileModificator", player_id: int, tile: "Tile.TileData"):
        pass
    
    @staticmethod
    def movement(modificator: "TileModificator", movement: int, tile: "Tile.TileData") -> int:
        return movement
    
    @staticmethod
    def additional_movement(modificator: "TileModificator", movement: int, tile: "Tile.TileData") -> int:
        return 0
    
    @staticmethod
    def bonus_movement(modificator: "TileModificator", movement: int, tile: "Tile.TileData") -> int:
        return 1
    
    @staticmethod
    def on_unit_enter(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def on_unit_exit(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData"):
        pass
    
    @staticmethod
    def on_building(modificator: "TileModificator", building: BuildingType, player_id: int, tile: "Tile.TileData"):
        pass

    @staticmethod
    def on_harvest(modificator: "TileModificator", player_id: int, tile: "Tile.TileData"):
        pass

    @staticmethod
    def on_terraform(modificator: "TileModificator", terraform: TerraForm, player_id: int, tile: "Tile.TileData"):
        pass

    @staticmethod
    def on_owner_change(modificator: "TileModificator", old_owner: int, new_owner: int, tile: "Tile.TileData"):
        pass

class TileModificator(GenericObject):
    type: TileModificatorType
    args: list[int]

    def __init__(self, tile_mod_type: TileModificatorType, args: list[int]):
        self.type = tile_mod_type
        self.args = args