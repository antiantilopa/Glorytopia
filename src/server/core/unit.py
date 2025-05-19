from shared.unit_types import AbilityIndexes, UnitType
from shared.unit import UnitData
from shared.tile_types import TileTypes
from pygame_tools_tafh import Vector2d
from .world import World
from math import floor, ceil
from .tile import Tile
from . import city as City
from . import player as Player
from enum import Enum

class Ability:
    index: int
    abilities: dict[int, type["Ability"]] = {}

    def __init_subclass__(cls, ind: AbilityIndexes):
        Ability.abilities[ind] = (cls)

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
    def defense_bonus(unit: "Unit") -> float:
        return 1

    @staticmethod
    def additional_move(unit: "Unit"):
        pass

    @staticmethod
    def retaliation_bonus(unit: "Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def retaliation_mitigate(unit: "Unit", defense_result: int) -> int:
        return defense_result

    @staticmethod
    def attack_bonus(unit: "Unit", attack_result: int) -> int:
        return attack_result
    
    @staticmethod
    def on_terrain_movement(unit: "Unit", tile: Tile, movement: int) -> int:
        return 0
    
    @staticmethod
    def get_vision_range(unit: "Unit") -> int:
        return 0
    
    @staticmethod
    def get_visibility(unit: "Unit") -> bool:
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
            if World.cities_mask[unit.pos.y][unit.pos.x]:
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

class Unit(UnitData):
    attached_city: "City.City"
    units: list["Unit"] = []

    def __init__(self, utype: UnitType, owner: int, pos: Vector2d, attached_city: "City.City"):
        super().__init__(utype, owner, pos)
        self.attached_city = attached_city
        Unit.units.append(self)
    
    def refresh(self):
        self.moved = False
        self.attacked = False

    def get_movements(self) -> list[Vector2d, int]:
        s_poses = [[self.pos, self.utype.movement]]
        e_poses = []

        def is_in(pos: Vector2d, array: list[tuple[Vector2d, any]]) -> int:
            for poss in array:
                if poss[0] == pos:
                    return array.index(poss)
            return -1

        def get_mv(movement: float, tile: Tile) -> float:
            res = 0 if tile.ttype.stops_movement else movement - 1 * (1 - 0.5 * tile.has_road)
            for ability in self.utype.abilities:
                res = max(res, Ability.abilities[ability].on_terrain_movement(self, tile, movement))
            return res
        while len(s_poses) != 0:
            s_pos = s_poses.pop(0)
            if s_pos[1] <= 0:
                if not World.object.unit_mask[s_pos[0].y][s_pos[0].x]:
                    e_poses.append(s_pos)
                continue
            for (dx, dy) in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)):
                n_pos = s_pos[0] + Vector2d(dx, dy)
                if not World.object.is_in(n_pos):
                    continue
                tmp = False
                if World.object.unit_mask[n_pos.y][n_pos.x]:
                    for unit in Unit.units:
                        if unit.pos == n_pos:
                            if unit.owner != self.owner:
                                tmp = True
                            break
                if tmp is True:
                    continue
                if World.object.get(n_pos).ttype.is_water != self.utype.water:
                    continue
                available = False
                for tech in Player.Player.players[self.owner].techs:
                    if World.object.get(n_pos).ttype in tech.accessable:
                        available = True
                        break
                if not available:
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
                s_poses.append([n_pos, next_mv])
            if World.object.unit_mask[s_pos[0].y][s_pos[0].x] is False:
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
                return [unit.pos for unit in self.get_attacks()]
        else:
            result = [i[0] for i in self.get_movements()]
            if not self.attacked:
                result += [unit.pos for unit in self.get_attacks()]
            return result
        
    # calculates attack when self is attacker, and other is defender.
    def calc_attack(self, other: "Unit") -> tuple[int, int]:
        defense_bonus = 1
        for tech in Player.Player.players[other.owner].techs:
            if World.object.get(other.pos) in tech.defence:
                defense_bonus = 1.5
                break
        for ability in self.utype.abilities:
            defense_bonus *= Ability.abilities[ability].defense_bonus(other)

        attack_force = self.utype.attack * (self.health / self.utype.health)
        defense_force = other.utype.defense * (other.health / other.utype.health) * defense_bonus
        total_damage = attack_force + defense_force
        attack_result = ((attack_force / total_damage) * self.utype.attack * 4.5)
        defense_result = ((defense_force / total_damage) * other.utype.defense * 4.5)

        # Fucking python rounds it fucking wrong!
        # 0.5 -> 0; 1.5 -> 2; 2.5 -> 2; 3.5 -> 4
        # Fuck you, python :)
        def round_to_nearest(x: float) -> int:
            if x - floor(x) < 0.5:
                return floor(x)
            else:
                return ceil(x)
        attack_result = round_to_nearest(attack_result)
        defense_result = round_to_nearest(defense_result)

        result = [0, 0]
        result[0] = attack_result
        if other.health > attack_result:
            if (self in other.get_attacks()):
                for ability in other.utype.abilities:
                    defense_result = Ability.abilities[ability].retaliation_bonus(other, defense_result)
                for ability in self.utype.abilities:
                    defense_result = Ability.abilities[ability].retaliation_mitigate(self, defense_result)
                result[1] = defense_result
        print(result)
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
                    attack, defense = self.calc_attack(unit)
                    unit.recv_damage(attack)
                    self.recv_damage(defense)
                    if unit.health <= 0 and self.utype.attack_range == 1:
                        World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 0
                        self.pos = unit.pos
                    if unit.health <= 0:
                        for ability in self.utype.abilities:
                            Ability.abilities[ability].after_kill(self, unit)

                    for ability in self.utype.abilities:
                        Ability.abilities[ability].after_attack(self, unit)
                    break
        else:
            World.object.unit_mask[self.pos.y][self.pos.x] = 0
            self.pos = pos
            World.object.unit_mask[self.pos.y][self.pos.x] = 1
    
    def heal(self):
        if World.object.get(self.pos).owner == self.owner:
            self.health = min(self.health + 4, self.utype.health)
        else:
            self.health = min(self.health + 2, self.utype.health)
    
    def get_vision_range(self) -> int:
        vision = 2 if World.object.get(self.pos).ttype == TileTypes.mountain else 1
        for ability in self.utype.abilities:
            vision = max(vision, Ability.abilities[ability].get_vision_range(self))
        return vision

    def get_visibility(self) -> bool:
        visibility = 1
        for ability in self.utype.abilities:
            visibility = visibility and Ability.abilities[ability].get_visibility(self)
        return visibility