from pathlib import Path

from netio.util.lazy_reference import LazyRef
from shared.effect import Effect, EffectType
from .modificator import TileModificatorType
from .globals.mod_versions import ModConfig, ModVersions
from .asset_types import BuildingType, Nation, ResourceType, TechNode, UnitType, TileType, TerraForm
from .util.json import from_file
import json, os
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

    if nations.exists():
        for nation_path in nations.iterdir():
            nation = load_nation(nation_path)
            Nation.add(nation)
    
def load_mains():
    for path in MODS_PATH.iterdir():
        if not (path / "main.py").exists():
            continue
        try:
            __import__(str(path / "main").replace(os.sep, "."), fromlist=str(path).split(os.sep)).load_mod()
        except Exception as e:
            print(f"Error loading main.py from mod {path.name}: {e}")
            raise e

def load_texture_assignments():
    for path in MODS_PATH.iterdir():
        if not (path / "texture_assign").exists():
            continue
        for file in (path / "texture_assign").iterdir():
            if file.suffix != ".py":
                continue
            try:
                __import__(str(path / "texture_assign" / file.name).removesuffix(".py").replace(os.sep, "."), fromlist=str(path).split(os.sep))
            except Exception as e:
                print(f"Error loading texture assignment {file.name} from mod {path.name}: {e}")
                raise e

def load_complex_types_full():
    for path in MODS_PATH.iterdir():
        for complex_name in ("effects", "abilities", "tile_modificators"):
            if not (path / complex_name / "config.json").exists():
                continue
            complices = json.load(open(path / complex_name / "config.json"))
            for complex in complices:
                if "file_name" not in complex:
                    print(f"Error loading {complex_name} from mod {path.name}: {e}")
                    raise KeyError(f"file_name keyword not found in {complex_name}:{complex}")
                try:
                    __import__(str(path / complex_name / complex["file_name"]).removesuffix(".py").replace(os.sep, "."), fromlist=str(path).split(os.sep))
                except Exception as e:
                    print(f"Error loading {complex_name} {complex["file_name"]} from mod {path.name}: {e}")
                    raise e

def load_complex_type_names():
    for path in MODS_PATH.iterdir():
        try:
            if (path / "effects" / "config.json").exists():
                effects = json.load(open(path / "effects" / "config.json"))
                for effect_json in effects:
                    EffectType.add(EffectType(effect_json["name"]))
            if (path / "tile_modificators" / "config.json").exists():
                modificators = json.load(open(path / "tile_modificators" / "config.json"))
                for modificator_json in modificators:
                    TileModificatorType.add(TileModificatorType(modificator_json["name"]))
        except Exception as e:
            print(f"Error loading complex's name from mod {path.name}: {e}")
            raise e

def load_actions():
    for path in MODS_PATH.iterdir():
        if not (path / "actions").exists():
            continue
        for file in (path / "actions").iterdir():
            if file.suffix != ".py":
                continue
            try:
                __import__(str(path / "actions" / file.name).removesuffix(".py").replace(os.sep, "."), fromlist=str(path).split(os.sep))
            except Exception as e:
                print(f"Error loading actions assignment {file.name} from mod {path.name}: {e}")
                raise e

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


