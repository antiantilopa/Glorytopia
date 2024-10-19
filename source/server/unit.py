from shared.unit_types import Abilities
from shared.unit import UnitData
from shared.vmath import Vector2d
from core.tile import World, Tile
from enum import Enum

class Unit(UnitData):
    
    def refresh(self):
        self.moved = False
        self.attacked = False

    def doesReach(self, pos: Vector2d, world: World):
        pass
    
    def getMovements(self, world: World) -> list[Vector2d]:
        s_poses = [(self.pos, self.utype.movement)]
        e_poses = []
        def isIn(pos: Vector2d, array: list):
            for poss in array:
                if poss[0] == pos:
                    return array.index(poss)
            return -1
        def get_mv(movement: int, tile: Tile):
            if tile.hasroad:
                return movement - 0.5
            if tile.ttype.stopsmovement:
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
                if not world.isIn(n_pos):
                    continue
                next_mv = get_mv(s_pos[1], world.get(s_pos[0]))
                if next_mv < 0:
                    continue
                r = isIn(n_pos, s_poses)
                if r != -1:
                    s_poses[r][1] = max(s_poses[r][1], next_mv)
                    continue
                r = isIn(n_pos, e_poses)
                if r != -1:
                    if e_poses[r][1] < next_mv:
                        e_poses.pop(r)
                        s_poses.append((n_pos, next_mv))
                    continue
                s_poses.append((n_pos, next_mv))
            e_poses.append(s_pos)
            s_poses.remove(s_pos)
    
    def getAttacks(self, units: list["Unit"]) -> list["Unit"]:
        result = []
        for unit in units:
            if max((unit.pos - self.pos).x, (unit.pos - self.pos).y) <= self.utype.attackrange:
                result.append(unit)
        return result

    def getPossibleMoves(self, world: World, units: list["Unit"]) -> list[Vector2d]:
        if self.moved:
            if self.attacked:
                return []
            if Abilities.dash in self.utype.abilities:
                return [unit.pos for unit in self.getAttacks(units)]
        else:
            result = self.getMovements(world)
            if not self.attacked:
                result += [unit.pos for unit in self.getAttacks(units)]
            return result

    def calc_attack(self):
        # TODO calculate attack damage after all modifiers
        raise NotImplementedError
    
    def calc_defense(self):
        # TODO calculate defense after all modifiers
        raise NotImplementedError
    
    def calc_damage(self, damage: int):
        # TODO apply damage to unit
        raise NotImplementedError