from netio import GenericType
from . import tile as Tile
from . import unit as Unit

class Ability(GenericType):
    # Never should be serialized.
    name: str

    ID = 0

    def __init_subclass__(cls):
        ability = cls(cls.name)
        Ability.add(ability)

    def __init__(self, name):
        self.name = name
        self.id = Ability.ID
        Ability.ID += 1

    @staticmethod
    def after_movement(unit: "Unit.Unit"):
        pass

    @staticmethod
    def after_attack(unit: "Unit.Unit", other: "Unit.Unit"):
        pass

    @staticmethod
    def after_kill(unit: "Unit.Unit", other: "Unit.Unit"):
        pass

    @staticmethod
    def defense_bonus(unit: "Unit.Unit") -> float:
        return 1

    @staticmethod
    def attack_bonus(unit: "Unit.Unit") -> float:
        return 1

    @staticmethod
    def additional_move(unit: "Unit.Unit"):
        pass

    @staticmethod
    def retaliation_bonus(unit: "Unit.Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def retaliation_mitigate(unit: "Unit.Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def attack_bonus(unit: "Unit.Unit", attack_result: int) -> int:
        return attack_result
    
    @staticmethod
    def on_terrain_movement(unit: "Unit.Unit", tile: "Tile.Tile", movement: int) -> int:
        return 0
    
    @staticmethod
    def save_moved(unit: "Unit.Unit") -> bool:
        return False
    
    @staticmethod
    def save_attacked(unit: "Unit.Unit") -> bool:
        return False

    @staticmethod
    def get_vision_range(unit: "Unit.Unit") -> int:
        return 0
    
    @staticmethod
    def get_visibility(unit: "Unit.Unit", player_id: int) -> bool:
        return 1

    @staticmethod
    def additional_attack(unit: "Unit.Unit", other: "Unit.Unit") -> int:
        return 0

    @staticmethod
    def additional_defense(unit: "Unit.Unit", other: "Unit.Unit") -> int:
        return 0

    @staticmethod
    def on_start_turn(unit: "Unit.Unit"):
        pass

    @staticmethod
    def after_heal(unit: "Unit.Unit"):
        pass

    @staticmethod
    def additional_heal(unit: "Unit.Unit"):
        return 0
    
    @staticmethod
    def on_death(unit: "Unit.Unit"):
        pass

    @staticmethod
    def on_spawn(unit: "Unit.Unit"):
        pass

    @staticmethod
    def on_end_turn(unit: "Unit.Unit"):
        pass
    