from engine_antiantilopa import Vector2d
from serializator.net import flags_to_int
from shared.asset_types import Nation, TechNode

SerializedPlayer = tuple[int, int, list[int], list[int], bool]

class PlayerData:
    id: int
    money: int
    vision: list[list[int]]
    techs: list[TechNode]
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
        self.techs.append(nation.base_tech)

    def to_serializable(self):
        return [
            self.id,
            self.money,
            [flags_to_int(*row) for row in self.vision],
            [tech.id for tech in self.techs], # super bad with mods. who cares now? TODO. maybe names?
            self.is_dead
        ]

    @staticmethod
    def from_serializable(serializable: SerializedPlayer) -> "PlayerData":
        player = PlayerData()
        # TODO BUG FUCK IT! TAFH, I BELIEVE IN YOUR NEW SUPER METHOD !!!
        return player