from pathlib import Path

from netio.util.lazy_reference import LazyRef
from shared.effect import Effect, EffectType
from .globals.mod_versions import ModConfig, ModVersions
from .asset_types import BuildingType, Nation, ResourceType, TechNode, UnitType, TileType, TerraForm
from .util.json import from_file
import json
from typing import TypeVar

T = TypeVar("T")

    
MODS_PATH = Path("./mods")

def load_nation(path: Path) -> Nation:
    print(path)
    units = path / "units"
    tiles = path / "tiles"
    buildings = path / "buildings"
    resources = path / "resources"
    terraforms = path / "terraforms"
    techs = path / "techs"

    nation = from_file(Nation, path / "config.json")
    Nation.add(nation)

    if tiles.exists():
        for tile_json in tiles.iterdir():
            tile = from_file(TileType, str(tile_json))
            TileType.add(tile)

    if units.exists():
        for unit_json in units.iterdir():
            unit = from_file(UnitType, str(unit_json))
            UnitType.add(unit)

    if buildings.exists():
        for building_json in buildings.iterdir():
            building = from_file(BuildingType, str(building_json))
            BuildingType.add(building)

    if resources.exists():
        for resource_json in resources.iterdir():
            resource = from_file(ResourceType, str(resource_json))
            ResourceType.add(resource)  
    
    if terraforms.exists():
        for terraform_json in terraforms.iterdir():
            terraform = from_file(TerraForm, str(terraform_json))
            TerraForm.add(terraform)

    if techs.exists():
        for tech_json in techs.iterdir():
            tech = from_file(TechNode, str(tech_json))
            TechNode.add(tech)

    return nation
        

def load_mod(path: Path):
    units = path / "units"
    tiles = path / "tiles"
    buildings = path / "buildings"
    resources = path / "resources"
    terraforms = path / "terraforms"
    techs = path / "techs"
    nations = path / "nations"

    config = from_file(ModConfig, path / "config.json")
    ModVersions.mods.append(config)

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

    for nation_path in nations.iterdir():
        nation = load_nation(nation_path)
        Nation.add(nation)
    
def load_mains():
    for path in MODS_PATH.iterdir():
        try:
            __import__(str(path / "main").replace("\\", "."), fromlist=str(path).split("\\")).load_mod()
        except Exception as e:
            print(f"Error loading mod {path.name}: {e}")

            
def load_effects_and_abilities_full():
    for path in MODS_PATH.iterdir():
        try:
            effects = json.load(open(path / "effects" / "config.json"))
            for effect in effects:
                __import__(str(path / "effects" / effect["file_name"]).removesuffix(".py").replace("\\", "."), fromlist=str(path).split("\\"))
            abilities = json.load(open(path / "abilities" / "config.json"))
            for ability in abilities:
                __import__(str(path / "abilities" / ability["file_name"]).removesuffix(".py").replace("\\", "."), fromlist=str(path).split("\\"))
        except Exception as e:
            print(f"Error loading mod {path.name}: {e}")

def load_effects_names():
    for path in MODS_PATH.iterdir():
        effects = json.load(open(path / "effects" / "config.json"))
        for effect in effects:
            EffectType.add(EffectType(effect["name"]))

def load_assets():
    for mod_path in MODS_PATH.iterdir():
        load_mod(mod_path)
    remove_ref()
    TechNode.assign()

def remove_ref():
    for cls in (TileType, UnitType, BuildingType, ResourceType, TerraForm, TechNode, Nation):
        for obj in cls.values():
            for key, value in obj.__dict__.items():
                if isinstance(value, LazyRef):
                    setattr(obj, key, value.cls.get(value.name))