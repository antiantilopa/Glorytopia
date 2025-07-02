from shared.unit_types import UnitType
from shared.unit import UnitData
from shared.tile_types import TileTypes
from engine_antiantilopa import Vector2d
from .world import World
from math import floor, ceil
from .tile import Tile
from . import city as City
from . import player as Player
from .ability import Ability
from .updating_object import UpdatingObject

class Unit(UnitData, UpdatingObject):
    attached_city: "City.City"
    previous_pos: Vector2d

    units: list["Unit"] = []
    def __init__(self, utype: UnitType, owner: int, pos: Vector2d, attached_city: "City.City"):
        UpdatingObject.__init__(self)
        UnitData.__init__(self, utype, owner, pos)
        self.attached_city = attached_city
        self.previous_pos = Vector2d(-1, -1)
        Unit.units.append(self)
    
    def refresh(self):
        self.moved = False
        self.attacked = False

    def get_movements(self) -> list[Vector2d, int]:
        s_poses: list[tuple[Vector2d, float]] = [(self.pos, self.utype.movement)]
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
            if World.object.unit_mask[s_pos[0].y][s_pos[0].x] == False:
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
        self.attacked = True
        if World.object.unit_mask[pos.y][pos.x]:
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
            for ability in self.utype.abilities:
                Ability.abilities[ability].after_movement(self)
    
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
    
    def destroy(self):
        if self.attached_city is not None:
            self.attached_city.fullness -= 1
        World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 0
        for unit in Unit.units:
            if unit.pos == self.pos and unit != self:
                World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 1
                break
        Unit.units.remove(self)
        Player.Player.players[self.owner].units.remove(self)
        UpdatingObject.destroy(self)
        del self
    
    def __setattr__(self, name, value):
        if name == "previous_pos":
            object.__setattr__(self, "previous_pos", value)
            return
        if name == "pos":
            if hasattr(self, "pos"):
                object.__setattr__(self, "previous_pos", self.pos)
            else:
                print(value)
                object.__setattr__(self, "previous_pos", value)
        return UpdatingObject.__setattr__(self, name, value)

    def refresh_updated(self):
        self.previous_pos = self.pos
        return super().refresh_updated()