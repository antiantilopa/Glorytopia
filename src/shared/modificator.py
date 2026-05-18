from typing import Annotated
from netio import Serializable, GenericType, SerializeField
from shared.asset_types import BuildingType, TerraForm
from shared.generic_object import GenericObject
from . import tile as Tile
from . import unit as Unit

class TileModificatorType(GenericType):
    name: str

    ID = 0
    
    def __init_subclass__(cls):
        etype = cls(cls.name)
        TileModificatorType.add(etype)

    def __init__(self, name = ""):
        self.name = name
        self.id = TileModificatorType.ID
        TileModificatorType.ID += 1

    @staticmethod
    def on_yaderka_boom(modificator: "TileModificator", tile: "Tile.TileData", player_id: int):
        pass
    
    @staticmethod
    def movement(modificator: "TileModificator", tile: "Tile.TileData", movement: int) -> int:
        return movement
    
    @staticmethod
    def additional_movement(modificator: "TileModificator", tile: "Tile.TileData", movement: int) -> int:
        return 0
    
    @staticmethod
    def bonus_movement(modificator: "TileModificator", tile: "Tile.TileData", movement: int) -> int:
        return 1
    
    @staticmethod
    def ignore_water(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData") -> int:
        return 0
    
    @staticmethod
    def ignore_stop_movement(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData") -> int:
        return 0
    
    @staticmethod
    def stop_movement(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData") -> bool:
        return 0
    
    @staticmethod
    def on_unit_enter(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData"):
        pass

    @staticmethod
    def on_unit_exit(modificator: "TileModificator", tile: "Tile.TileData", unit: "Unit.UnitData"):
        pass
    
    @staticmethod
    def on_building(modificator: "TileModificator", tile: "Tile.TileData", building: BuildingType, player_id: int):
        pass

    @staticmethod
    def on_harvest(modificator: "TileModificator", tile: "Tile.TileData", player_id: int):
        pass

    @staticmethod
    def on_terraform(modificator: "TileModificator", tile: "Tile.TileData", terraform: TerraForm, player_id: int):
        pass

    @staticmethod
    def on_owner_change(modificator: "TileModificator",  tile: "Tile.TileData", old_owner: int, new_owner: int):
        pass

    @staticmethod
    def on_end_turn(modificator: "TileModificator", tile: "Tile.TileData", ):
        pass

    @staticmethod
    def on_start_turn(modificator: "TileModificator", tile: "Tile.TileData", player_id: int):
        pass

    @staticmethod
    def on_spawn(modificator: "TileModificator", tile: "Tile.TileData"):
        pass

class TileModificator(GenericObject):
    tmtype: Annotated[TileModificatorType, SerializeField()]
    args: Annotated[list[int], SerializeField()]

    def __init__(self, tile_mod_type: TileModificatorType, args: list[int], tile: "Tile.TileData"):
        self.tmtype = tile_mod_type
        self.args = args
        self.tmtype.on_spawn(self, tile)