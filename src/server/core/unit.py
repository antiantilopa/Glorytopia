from shared.unit_types import AbilityIndexes, UnitType
from shared.unit import UnitData
from pygame_tools_tafh import Vector2d
from .world import World
from math import floor, ceil
from .tile import Tile
from . import city as City
from enum import Enum

class Ability:
    index: int
    abilities: dict[int, type["Ability"]] = {}

    def __init_subclass__(cls, ind: AbilityIndexes):
        Ability.abilities[ind.value] = (cls)

    @staticmethod
    def after_movement(unit: "Unit"):
        pass

    @staticmethod
    def after_attack(unit: "Unit", other: "Unit"):
        pass

    @staticmethod
    def after_kill(unit: "Unit", other: "Unit"):
        pass

    @staticmethod
    def defence_bonus(unit: "Unit"):
        pass

    @staticmethod
    def additional_move(unit: "Unit"):
        pass

class Abilities:

    class Dash(Ability, ind = AbilityIndexes.dash):

        @staticmethod
        def after_movement(unit):
            unit.attacked = False
    
    class Fortify(Ability, ind = AbilityIndexes.fortify):

        @staticmethod
        def defence_bonus(unit):
            res = 1
            if World.object.cities_mask[unit.pos.y][unit.pos.x]:
                res = 1.5
                for city in City.City.cities:
                    if city.pos == unit.pos:
                        if city.walls is True:
                            res = 2
                        else:
                            break
            return res

    class Escape(Ability, ind = AbilityIndexes.escape):

        @staticmethod
        def after_attack(unit: "Unit", _):
            unit.moved = False

    class Stiff(Ability, ind = AbilityIndexes.stiff):
        index = AbilityIndexes.stiff

class Unit(UnitData):
    units: list["Unit"] = []

    def __init__(self, utype: UnitType, owner: int, pos: Vector2d):
        super().__init__(utype, owner, pos)
        Unit.units.append(self)
    
    def refresh(self):
        self.moved = False
        self.attacked = False

    def get_movements(self) -> list[Vector2d]:
        s_poses = [[self.pos, self.utype.movement]]
        e_poses = []

        def is_in(pos: Vector2d, array: list[tuple[Vector2d, any]]) -> int:
            for poss in array:
                if poss[0] == pos:
                    return array.index(poss)
            return -1

        def get_mv(movement: float, tile: Tile) -> float:
            if tile.has_road:
                return movement - 0.5
            if tile.ttype.stops_movement:
                return 0
            else:
                return movement - 1

        while len(s_poses) != 0:
            s_pos = s_poses.pop(0)
            if s_pos[1] <= 0:
                e_poses.append(s_pos)
                continue
            for (dx, dy) in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)):
                n_pos = s_pos[0] + Vector2d(dx, dy)
                if not World.object.is_in(n_pos):
                    continue
                next_mv = get_mv(s_pos[1], World.object.get(n_pos))
                if next_mv < 0:
                    continue
                r = is_in(n_pos, s_poses)
                if r != -1:
                    s_poses[r][1] = max(s_poses[r][1], next_mv)
                    continue
                r = is_in(n_pos, e_poses)
                if r != -1:
                    if e_poses[r][1] < next_mv:
                        e_poses.pop(r)
                        s_poses.append([n_pos, next_mv])
                    continue
                if World.object.get(n_pos).ttype.is_water != self.utype.water:
                    continue
                s_poses.append([n_pos, next_mv])
            e_poses.append(s_pos)
        return e_poses
    
    def get_attacks(self) -> list["Unit"]:
        result = []
        for unit in Unit.units:
            if unit.owner != self.owner:
                if max((unit.pos - self.pos).x, (unit.pos - self.pos).y) <= self.utype.attack_range:
                    result.append(unit)
        return result

    def get_possible_moves(self) -> list[Vector2d]:
        if self.moved:
            if self.attacked:
                return []
            else:
                return self.get_attacks()
        else:
            result = [i[0] for i in self.get_movements()]
            if not self.attacked:
                result += [unit.pos for unit in self.get_attacks()]
            return result
        
    # calculates attack when self is attacker, and other is defender.
    def calc_attack(self, other: "Unit") -> tuple[int, int]:
        defense_bonus = 1
        for ability in self.utype.abilities:
            defense_bonus *= Ability.abilities[ability].defence_bonus(other)

        attack_force = self.utype.attack * (self.health / self.utype.health)
        defense_force = other.utype.defense * (other.health / other.utype.health) * defense_bonus
        total_damage = attack_force + defense_force
        attack_result = ceil((attack_force / total_damage) * self.utype.attack * 4.5)
        defense_result = floor((defense_force / total_damage) * other.utype.defense * 4.5)

        result = [0, 0]
        result[0] = attack_result
        if other.health > 0:
            if (self in other.get_attacks()) and not (AbilityIndexes.stiff in other.utype.abilities):
                result[1] = defense_result
        return result
    
    def recv_damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def move(self, pos: Vector2d):
        if not (pos in self.get_possible_moves()):
            return 
        self.moved = True
        if World.object.unit_mask[pos.y][pos.x]:
            self.attacked = True
            for unit in Unit.units:
                if unit.pos == pos:
                    attack, defence = self.calc_attack(unit)
                    unit.recv_damage(attack)
                    self.recv_damage(defence)
                    if unit.health <= 0 and self.utype.attack_range == 1:
                        World.object.unit_mask[self.pos.y][self.pos.x] = 0
                        self.pos = unit.pos
                    if unit.health <= 0 and self.utype.attack_range > 1:
                        World.object.unit_mask[unit.pos.y][unit.pos.x] = 0
                    if unit.health <= 0:
                        for ability in self.utype.abilities:
                            Ability.abilities[ability].after_kill(self, unit)

                    for ability in self.utype.abilities:
                        Ability.abilities[ability].after_attack(self, unit)
        else:
            World.object.unit_mask[self.pos.y][self.pos.x] = 0
            self.pos = pos