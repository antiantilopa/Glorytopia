from pathlib import Path

from .asset_types import BuildingType, ResourceType, TechNode, UnitType, TileType, TerraForm
from .util.json import from_file
from typing import TypeVar

T = TypeVar("T")

    
MODS_PATH = Path("./mods")

def load_mod(path: Path):
    units = path / "units"
    tiles = path / "tiles"
    buildings = path / "buildings"
    resources = path / "resources"
    terraforms = path / "terraforms"
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
    
    for terraform_json in terraforms.iterdir():
        terraform = from_file(TerraForm, str(terraform_json))
        TerraForm.add(terraform)

    for tech_json in techs.iterdir():
        tech = from_file(TechNode, str(tech_json))
        TechNode.add(tech)
    
def load_mains():
    for path in MODS_PATH.iterdir():
        try:
            __import__(str(path / "main").replace("\\", "."), fromlist=str(path).split("\\")).load_mod()
            for ability_path in (path / "abilities").iterdir():
                __import__(str(ability_path).removesuffix(".py").replace("\\", "."), fromlist=str(path).split("\\"))
            __import__(str(path / "main").replace("\\", "."), fromlist=str(path).split("\\")).load_mod()
        except Exception as e:
            print(f"Error loading mod {path.name}: {e}")
            
def load_assets():
    for mod_path in MODS_PATH.iterdir():
        load_mod(mod_path)

    TechNode.assign()