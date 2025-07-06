from shared.unit_types import AbilityIndexes
from .world import World
from .tile import Tile
from . import city as City
from . import unit as Unit

class Ability:
    index: int
    abilities: dict[int, type["Ability"]] = {}

    def __init_subclass__(cls, ind: AbilityIndexes):
        Ability.abilities[ind] = (cls)

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
    def on_terrain_movement(unit: "Unit.Unit", tile: Tile, movement: int) -> int:
        return 0
    
    @staticmethod
    def get_vision_range(unit: "Unit.Unit") -> int:
        return 0
    
    @staticmethod
    def get_visibility(unit: "Unit.Unit") -> bool:
        return 1
    

class Abilities:

    class Dash(Ability, ind = AbilityIndexes.dash):

        @staticmethod
        def after_movement(unit):
            unit.attacked = False
    
    class Fortify(Ability, ind = AbilityIndexes.fortify):

        @staticmethod
        def defense_bonus(unit):
            res = 1
            if World.object.cities_mask[unit.pos.y][unit.pos.x]:
                res = 1.5
                for city in City.City.cities:
                    if city.pos == unit.pos:
                        if city.walls == True:
                            res = 4
                            break
                        else:
                            break
            return res

    class Escape(Ability, ind = AbilityIndexes.escape):

        @staticmethod
        def after_attack(unit: "Unit.Unit", _):
            unit.moved = False

    class Stiff(Ability, ind = AbilityIndexes.stiff):
        index = AbilityIndexes.stiff
    
        @staticmethod
        def retaliation_bonus(*_):
            return 0

    class Persist(Ability, ind = AbilityIndexes.persist):
        index = AbilityIndexes.persist

        @staticmethod
        def after_kill(unit, other):
            unit.attacked = False
    
    class Creep(Ability, ind = AbilityIndexes.creep):
        index = AbilityIndexes.creep

        @staticmethod
        def on_terrain_movement(unit, tile, movement):
            return movement - 1 * (1 - 0.5 * tile.has_road)
    
    class Scout(Ability, ind = AbilityIndexes.scout):
        index = AbilityIndexes.scout

        @staticmethod
        def get_vision_range(unit):
            return 2

    class Hide(Ability, ind = AbilityIndexes.hide):
        index = AbilityIndexes.hide

        @staticmethod
        def get_visibility(unit):
            return 0
    
    class Infiltrate(Ability, ind = AbilityIndexes.infiltrate):
        index = AbilityIndexes.infiltrate

        def infiltrate(city: "City.City"):
            pass
            # TODO: implement infiltrate ability

        @staticmethod
        def after_movement(unit):
            if World.object.cities_mask[unit.pos.y][unit.pos.x]:
                for city in City.City.cities:
                    if city.pos == unit.pos:
                        if city.owner != unit.owner:
                            unit.health = 0
                            Abilities.Infiltrate.infiltrate(city)
                            break
                        else:
                            break
        
        @staticmethod
        def after_attack(unit, other):
            if World.cities_mask[other.pos.y][other.pos.x]:
                for city in City.City.cities:
                    if city.pos == unit.pos:
                        if city.owner != unit.owner:
                            unit.health = 0
                            Abilities.Infiltrate.infiltrate(city)
                            break
                        else:
                            break
    
    class Convert(Ability, ind = AbilityIndexes.convert):
        index = AbilityIndexes.convert

        @staticmethod
        def after_attack(unit, other):

            if other.attached_city is not None and other.attached_city.owner == other.owner:
                other.attached_city.fullness -= 1
            other.attached_city = None
            other.owner = unit.owner
            other.attacked = True
            other.moved = True
        
        @staticmethod
        def retaliation_mitigate(unit, defense_result):
            return 0
    
    class Heal(Ability, ind = AbilityIndexes.heal):
        index = AbilityIndexes.heal

        #TODO: implement heal ability