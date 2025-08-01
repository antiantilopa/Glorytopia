from .generic_types import GenericType
from .util.reference import Ref

class UnitType(GenericType["UnitType"]):
    id: int
    name: str
    health: int
    attack: float
    defense: float
    movement: float
    attack_range: int
    cost: int
    water: bool
    abilities: list[str]

    ID = 0

    def __init__(self, 
                 name: str = "default", 
                 health: int = 0, 
                 attack: float = 0, 
                 defense: float = 0, 
                 movement: int = 0, 
                 attack_range: int = 0,
                 cost: int = 0, 
                 water: bool = False, 
                 abilities: list[str] = []) -> None:
        self.id = UnitType.ID
        UnitType.ID += 1
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.movement = movement
        self.attack_range = attack_range
        self.cost = cost
        self.water = water
        self.abilities = abilities

class TileType(GenericType["TileType"]):
    first_thing_first_ima_say_all_the_word_inside_my_head_im_fired_up_and_tired_off_the_way_that_things_have_been_of_yuyuyyuyuyu: bool = False
    id: int
    name: str
    is_water: bool
    stops_movement: bool
    vision_range: int

    ID = 0
    
    def __init__(self, 
                 name: str = "default", 
                 is_water: bool = 0,
                 stops_movement: bool = 0,
                 vision_range: int = 1) -> None:
        self.id = TileType.ID
        TileType.ID += 1
        self.name = name
        self.is_water = is_water
        self.stops_movement = stops_movement
        self.vision_range = vision_range

    def __repr__(self) -> str:
        return self.name

class BuildingType(GenericType["BuildingType"]):
    id: int
    name: str
    ttypes: list[TileType]
    required_resource: "ResourceType|None"
    cost: int
    population: int
    adjacent_bonus: "BuildingType|None"

    ID = 0

    def __init__(self, 
                 name :str = "default",
                 ttypes: list[TileType] = [],
                 required_resource: "str | None" = None,
                 cost: int = 0,
                 population: int = 0,
                 adjacent_bonus: "str|None" = None) -> None:
        self.id = BuildingType.ID
        BuildingType.ID += 1
        self.name = name
        self.ttypes = [Ref(TileType).create(i) for i in ttypes]
        self.required_resource = Ref(ResourceType).create(required_resource)
        self.cost = cost
        self.population = population
        self.adjacent_bonus = Ref(BuildingType).create(adjacent_bonus)
    
    def __repr__(self) -> str:
        return self.name

class ResourceType(GenericType["ResourceType"]):
    id: int
    name: str
    ttypes: list[TileType]
    spawn_rates: dict[int, float] # spawn rate for each distance to nearest city. if distance is not in dict, then it is 0

    ID = 0

    def __init__(self, name: str = "default", ttypes: list[TileType] = [], spawn_rates: list[tuple[int, float]] = []) -> None:
        self.id = ResourceType.ID
        ResourceType.ID += 1
        self.name = name
        self.ttypes = [Ref(TileType).create(i) for i in ttypes]
        self.spawn_rates = dict(spawn_rates)

class TerraForm(GenericType["TerraForm"]):
    id: int
    name: str
    cost: int
    from_ttype: TileType
    from_resource: ResourceType|None
    to_ttype: TileType
    to_resource: ResourceType|None

    ID = 0

    def __init__(self, name: str = "default", cost: int = 0, from_ttype: str = "plain", from_resource: str = None, to_ttype: str = "plain", to_resource: str = None) -> None:
        self.id = TerraForm.ID
        TerraForm.ID += 1
        self.name = name
        self.cost = cost
        self.from_ttype = Ref(TileType).create(from_ttype)
        self.from_resource = Ref(ResourceType).create(from_resource)
        self.to_ttype = Ref(TileType).create(to_ttype)
        self.to_resource = Ref(ResourceType).create(to_resource)



class TechNode(GenericType["TechNode"]):
    id: int
    name: str
    cost: int
    parent: "TechNode|None"
    tier: int
    units: list[UnitType]
    buildings: list[BuildingType]
    achievements: list[0]
    harvestables: list[ResourceType]
    defence: list[TileType]
    accessable: list[TileType]
    terraforms: list[TerraForm]
    childs: list["TechNode"]

    ID = 0

    def __init__(self,
                 name: str = "default",
                 cost: int = 4,
                 parent: "str|None" = None,
                 tier: int = 0,
                 units: list[str] = [],
                 buildings: list[str] = [],
                 achievements: list[0] = [],
                 harvestables: list[str] = [],
                 defence: list[str] = [],
                 accessable: list[str] = [],
                 terraforms: list[str] = []) -> None:
        self.id = TechNode.ID
        TechNode.ID += 1
        self.name = name
        self.cost = cost
        if parent is not None:
            self.parent = Ref(TechNode).create(parent)
        else:
            self.parent = None
        self.tier = tier
        self.units = [Ref(UnitType).create(unit_name) for unit_name in units] 
        self.buildings = [Ref(BuildingType).create(building_name) for building_name in buildings] 
        self.achievements = achievements # TODO do not exist XD
        self.harvestables = [Ref(ResourceType).create(resource_name) for resource_name in harvestables]
        self.defence = [Ref(TileType).create(tile_name) for tile_name in defence]
        self.accessable = [Ref(TileType).create(tile_name) for tile_name in accessable]
        self.terraforms = [Ref(TerraForm).create(terraform_name) for terraform_name in terraforms]
        self.childs = []

    @staticmethod
    def assign(): 
        for tech1 in TechNode.values():
            for tech2 in TechNode.values():
                if tech2 == tech1.parent:
                    tech2.childs.append(tech1)
                    break
