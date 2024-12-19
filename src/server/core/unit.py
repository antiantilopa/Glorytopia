from shared.unit_types import Abilities, UnitType
from shared.unit import UnitData
from shared.vmath import Vector2d
from .globals import world
from math import floor, ceil
from .tile import Tile

class Unit(UnitData):
    units: list["Unit"] = []

    def __init__(self, utype: UnitType, owner: int, pos: Vector2d):
        super().__init__(utype, owner, pos)
        Unit.units.append(self)
    
    def refresh(self):
        self.moved = False
        self.attacked = False

    def get_movements(self) -> list[Vector2d]:
        s_poses = [(self.pos, self.utype.movement)]
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

        for s_pos in s_poses:
            if s_pos[1] <= 0:
                e_poses.append(s_pos)
                s_poses.remove(s_pos)
                continue
            for (dx, dy) in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)):
                n_pos = self.pos + Vector2d(dx, dy)
                if not world.is_in(n_pos):
                    continue
                next_mv = get_mv(s_pos[1], world.get(s_pos[0]))
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
                        s_poses.append((n_pos, next_mv))
                    continue
                s_poses.append((n_pos, next_mv))
            e_poses.append(s_pos)
            s_poses.remove(s_pos)
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
            if Abilities.dash in self.utype.abilities:
                return [unit.pos for unit in self.get_attacks()]
        else:
            result = self.get_movements()
            if not self.attacked:
                result += [unit.pos for unit in self.get_attacks()]
            return result
        
    # calculates attack when self is attacker, and other is defender.
    def calc_attack(self, other: "Unit"):
        defense_bonus = 1 # TODO

        attack_force = self.utype.attack * (self.health / self.utype.health)
        defense_force = other.utype.defense * (other.health / other.utype.health) * defense_bonus
        total_damage = attack_force + defense_force
        attack_result = ceil((attack_force / total_damage) * self.utype.attack * 4.5)
        defense_result = floor((defense_force / total_damage) * other.utype.defense * 4.5)

        other.recv_damage(attack_result)
        if other.health > 0:
            self.recv_damage(defense_result)
        else:
            if self.utype.attack_range == 1:
                self.pos = other.pos
    
    def recv_damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0