from engine_antiantilopa import Vector2d
from serializator.net import flags_to_int
from shared.asset_types import Nation, TechNode
from shared.io.serializable import Serializable

SerializedPlayer = tuple[int, int, list[int], list[int], bool]

class PlayerData(Serializable):
    id: int
    money: int
    vision: list[list[int]]
    techs: list[TechNode]
    serialized_fields = ["id", "money", "vision", "techs", "nation"]
    nation: Nation
    is_dead: bool

    def __init__(self, id: int, money: int, vision: list[list[int]], techs: list[TechNode], nation: Nation = None):
        self.id = id
        self.money = money
        self.vision = vision
        self.techs = techs
        self.nation = nation
        self.is_dead = False
    
    def set_nation(self, nation: Nation):
        self.nation = nation
        if nation is None:
            return
        self.techs.append(TechNode.get(nation.base_tech.name))
        # Wow... here Ref probles came out. we need to redo them TODO