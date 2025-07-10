from pathlib import Path

from .asset_types import BuildingType, ResourceType, TechNode, UnitType, TileType
from .util.json import from_file
from typing import TypeVar

T = TypeVar("T")

    
MODS_PATH = Path("./mods")

def load_mod(path: Path):
    units = path / "units"
    tiles = path / "tiles"
    buildings = path / "buildings"
    resources = path / "resources"
    techs = path / "techs"

    for tile_json in tiles.iterdir():
        tile = from_file(TileType, str(tile_json))
        TileType.add(tile)

    for unit_json in units.iterdir():
        unit = from_file(UnitType, str(unit_json))
        UnitType.add(unit)

    for building_json in buildings.iterdir():
        building = from_file(BuildingType, str(building_json))
        BuildingType.add(building)

    for resource_json in resources.iterdir():
        resource = from_file(ResourceType, str(resource_json))
        ResourceType.add(resource)  

    for tech_json in techs.iterdir():
        tech = from_file(TechNode, str(tech_json))
        TechNode.add(tech)

    TechNode.assign()

def load_assets():
    for mod_path in MODS_PATH.iterdir():
        load_mod(mod_path)