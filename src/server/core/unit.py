from shared.asset_types import UnitType, TileType
from shared.unit import SerializedUnit, UnitData
from engine_antiantilopa import Vector2d
from .world import World
from math import floor, ceil
from .tile import Tile
from . import city as City
from . import player as Player
from .ability import Ability
from .updating_object import UpdatingObject

SerializedUnit_ = tuple[int, int, tuple[int, int], int, int, tuple[int, int]|None, tuple[int, int]]

class Unit(UnitData, UpdatingObject):
    attached_city: "City.City"
    previous_pos: Vector2d

    units: list["Unit"] = []
    def __init__(self, utype: UnitType, owner: int, pos: Vector2d, attached_city: "City.City"):
        UpdatingObject.__init__(self)
        self.black_list.append("previous_pos")
        UnitData.__init__(self, utype, owner, pos)
        self.attached_city = attached_city
        self.previous_pos = Vector2d(-1, -1)
        Unit.units.append(self)
        World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 1
    
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
                res = max(res, Ability.get(ability).on_terrain_movement(self, tile, movement))
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
                if max(abs((unit.pos - self.pos).x), abs((unit.pos - self.pos).y)) <= self.utype.attack_range:
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
            if World.object.get(other.pos).ttype in tech.defence:
                defense_bonus = 1.5
                break
        for ability in other.utype.abilities:
            defense_bonus *= Ability.get(ability).defense_bonus(other)

        attack_value = other.utype.attack
        for ability in self.utype.abilities:
            attack_value += Ability.get(ability).additional_attack(other, self) 

        defense_value = other.utype.defense
        for ability in self.utype.abilities:
            defense_value += Ability.get(ability).additional_defense(self, other) 

        attack_force = self.utype.attack * (self.health / self.utype.health)
        defense_force = other.utype.defense * (other.health / other.utype.health) * defense_bonus
        total_damage = attack_force + defense_force
        attack_result = ((attack_force / total_damage) * self.utype.attack * 4.5)
        defense_result = ((defense_force / total_damage) * other.utype.defense * 4.5)

        # Fucking python rounds it fucking wrong!
        # 0.5 -> 0; 1.5 -> 2; 2.5 -> 2; 3.5 -> 4
        # Fuck you, python :) 
        def round_to_nearest(x: float) -> int:
            return floor(x + 0.5)
        attack_result = round_to_nearest(attack_result)
        defense_result = round_to_nearest(defense_result)

        result = [0, 0]
        result[0] = attack_result
        if other.health > attack_result:
            if (self in other.get_attacks()):
                for ability in other.utype.abilities:
                    defense_result = Ability.get(ability).retaliation_bonus(other, defense_result)
                for ability in self.utype.abilities:
                    defense_result = Ability.get(ability).retaliation_mitigate(self, defense_result)
                result[1] = defense_result
        return result
    
    def recv_damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def move(self, pos: Vector2d):
        if not (pos in self.get_possible_moves()):
            return 
        if World.object.unit_mask[pos.y][pos.x]:
            self.attacked = True
            save = False
            for ability in self.utype.abilities:
                save |= Ability.get(ability).save_moved(self)
            if not save:
                self.moved = True
            print(self.attacked)
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
                            Ability.get(ability).after_kill(self, unit)

                    for ability in self.utype.abilities:
                        Ability.get(ability).after_attack(self, unit)
                    break
        else:
            self.moved = True
            save = False
            for ability in self.utype.abilities:
                save |= Ability.get(ability).save_attacked(self)
            if not save:
                self.attacked = True
            World.object.unit_mask[self.pos.y][self.pos.x] = 0
            self.pos = pos
            World.object.unit_mask[self.pos.y][self.pos.x] = 1
            for ability in self.utype.abilities:
                Ability.get(ability).after_movement(self)
    
    def heal(self):
        if World.object.get(self.pos).owner == self.owner:
            self.health = min(self.health + 4, self.utype.health)
        else:
            self.health = min(self.health + 2, self.utype.health)
    
    def get_vision_range(self) -> int:
        vision = World.object.get(self.pos).ttype.vision_range
        for ability in self.utype.abilities:
            vision = max(vision, Ability.get(ability).get_vision_range(self))
        return vision

    def get_visibility(self) -> bool:
        visibility = 1
        for ability in self.utype.abilities:
            visibility = visibility and Ability.get(ability).get_visibility(self)
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

    def refresh_updated(self):
        self.previous_pos = self.pos
        return super().refresh_updated()
    
    def set_from_data(self, udata: UnitData):
        self.utype = udata.utype
        self.owner = udata.owner
        self.pos = udata.pos
        self.moved = udata.moved
        self.attacked = udata.attacked
        self.health = udata.health

    @staticmethod
    def from_serializable(serializable: SerializedUnit_) -> "Unit":
        udata = UnitData.from_serializable(serializable[0:5])
        unit = Unit(udata.utype, udata.owner, udata.pos, None)
        unit.previous_pos = Vector2d.from_tuple(serializable[6])
        unit.set_from_data(udata)
        if serializable[5] is not None:
            city = None
            for c in City.City.cities:
                if c.pos == Vector2d.from_tuple(serializable[5]):
                    city = c
                    break
            unit.attached_city = city
        else:
            unit.attached_city = None
        del udata
        return unit
    
    @staticmethod
    def do_serializable(serializable: SerializedUnit_) -> None:
        prev_pos = Vector2d.from_tuple(serializable[6])
        if prev_pos == Vector2d(-1, -1):
            new_unit = Unit.from_serializable(serializable)
            if new_unit.owner != 0:
                for player in Player.Player.players:
                    if player.id == new_unit.owner:
                        player.units.append(new_unit)
        else:
            udata = UnitData.from_serializable(serializable[0:5])
            found = False
            for unit in Unit.units:
                if unit.pos == prev_pos and unit.owner == udata.owner: # TODO BUG WTF check not only owner. this shit is so hard
                    found = True
                    
                    unit.set_from_data(udata)
                    break
            if not found:
                raise Exception("Imposiible unit data given")

    def to_serializable(self) -> SerializedUnit_:
        return UnitData.to_serializable(self) + [None if self.attached_city.pos is None else self.attached_city.pos.as_tuple(), self.previous_pos.as_tuple()]