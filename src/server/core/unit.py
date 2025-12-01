from shared.asset_types import UnitType, TileType
from shared.player import PlayerData_
from shared.unit import UnitData
from shared.util.position import Pos
from math import floor, ceil

from . import world as World
from . import tile as Tile
from . import city as City
from . import player as Player
from .ability import Ability

class Unit(UnitData):
    _attached_city: "City.City|None"

    units: list["Unit"] = []

    def __init__(self, utype: UnitType, owner: int, pos: Pos, attached_city: "City.City"):
        UnitData.__init__(self, utype, owner, pos)
        self.attached_city = attached_city
        Unit.units.append(self)
        World.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 1
        for ability in self.utype.abilities:
            Ability.get(ability).on_spawn(self)
        for effect in self.effects:
            effect.etype.on_spawn(effect, self)

    def refresh(self):
        for ability in self.utype.abilities:
            Ability.get(ability).on_start_turn(self)
        for effect in self.effects:
            effect.etype.on_start_turn(effect, self)
        self.moved = False
        self.attacked = False

    def get_movements(self) -> list[Pos, int]:
        s_poses: list[tuple[Pos, float]] = [(self.pos, self.utype.movement)]
        e_poses = []

        def is_in(pos: Pos, array: list[tuple[Pos, any]]) -> int:
            for poss in array:
                if poss[0] == pos:
                    return array.index(poss)
            return -1

        def get_mv(movement: float, tile: "Tile.Tile") -> float:
            res = 0 if tile.ttype.stops_movement else movement - 1 * (1 - 0.5 * tile.has_road)
            for ability in self.utype.abilities:
                res = max(res, Ability.get(ability).on_terrain_movement(self, tile, movement))
            for effect in self.effects:
                res = max(res, effect.etype.on_terrain_movement(effect, self, tile, movement))
            return res
        while len(s_poses) != 0:
            s_pos = s_poses.pop(0)
            if s_pos[1] <= 0:
                if not World.World.object.unit_mask[s_pos[0].y][s_pos[0].x]:
                    e_poses.append(s_pos)
                continue
            for (dx, dy) in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)):
                n_pos = s_pos[0] + Pos(dx, dy)
                if not World.World.object.is_in(n_pos):
                    continue
                tmp = False
                if World.World.object.unit_mask[n_pos.y][n_pos.x]:
                    for unit in Unit.units:
                        if unit.pos == n_pos:
                            if unit.owner != self.owner:
                                tmp = True
                            break
                if tmp is True:
                    continue
                if World.World.object.get(n_pos).ttype.is_water != self.utype.water:
                    continue
                available = False
                for tech in Player.Player.players[self.owner].techs:
                    if World.World.object.get(n_pos).ttype in tech.accessable:
                        available = True
                        break
                if not available:
                    continue
                next_mv = get_mv(s_pos[1], World.World.object.get(n_pos))
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
            if World.World.object.unit_mask[s_pos[0].y][s_pos[0].x] == False:
                e_poses.append(s_pos)
        return e_poses
    
    def get_attacks(self) -> list["Unit"]:
        result = []
        for unit in Unit.units:
            if unit.owner != self.owner:
                if max(abs((unit.pos - self.pos).x), abs((unit.pos - self.pos).y)) <= self.utype.attack_range:
                    result.append(unit)
        return result

    def get_possible_moves(self) -> list[Pos]:
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
            if World.World.object.get(other.pos).ttype in tech.defence:
                defense_bonus = 1.5
                break
        for ability in other.utype.abilities:
            defense_bonus *= Ability.get(ability).defense_bonus(other)
        for effect in other.effects:
            defense_bonus *= effect.etype.defense_bonus(effect, other)

        attack_bonus = 1
        for ability in self.utype.abilities:
            attack_bonus *= Ability.get(ability).attack_bonus(self)
        for effect in self.effects:
            attack_bonus *= effect.etype.attack_bonus(effect, self)

        defense_value = other.utype.defense
        for ability in other.utype.abilities:
            defense_value += Ability.get(ability).additional_defense(other, self) 
        for effect in other.effects:
            defense_value += effect.etype.additional_defense(effect, other, self) 

        attack_value = self.utype.attack
        for ability in self.utype.abilities:
            attack_value += Ability.get(ability).additional_attack(self, other) 
        for effect in self.effects:
            attack_value += effect.etype.additional_attack(effect, self, other) 

        attack_force = attack_value * (self.health / self.utype.health) * attack_bonus
        defense_force = defense_value * (other.health / other.utype.health) * defense_bonus
        total_damage = attack_force + defense_force
        attack_result = ((attack_force / total_damage) * attack_value * 4.5)
        defense_result = ((defense_force / total_damage) * defense_value * 4.5)

        # Fucking python rounds it fucking wrong!
        # 0.5 -> 0; 1.5 -> 2; 2.5 -> 2; 3.5 -> 4
        # Fuck you, python :) 
        def round_to_nearest(x: float) -> int:
            # and for any whole x,  round_to_nearest(x + 0.5) = x + 1 
            return floor(x + 0.5)
        attack_result = round_to_nearest(attack_result)
        defense_result = round_to_nearest(defense_result)

        result = [0, 0]
        result[0] = attack_result
        if other.health > attack_result:
            if (self in other.get_attacks()):
                # the order is very important, which is no good. TODO
                for ability in other.utype.abilities:
                    defense_result = Ability.get(ability).retaliation_bonus(other, defense_result)
                for effect in other.effects:
                    defense_result = effect.etype.retaliation_bonus(effect, other, defense_result)
                for ability in self.utype.abilities:
                    defense_result = Ability.get(ability).retaliation_mitigate(self, defense_result)
                for effect in self.effects:
                    defense_result = effect.etype.retaliation_mitigate(effect, self, defense_result)
                result[1] = defense_result
        return result
    
    def recv_damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def move(self, pos: Pos):
        if not (pos in self.get_possible_moves()):
            return 
        if World.World.object.unit_mask[pos.y][pos.x]:
            self.attacked = True
            save = False
            for ability in self.utype.abilities:
                save |= Ability.get(ability).save_moved(self)
            for effect in self.effects:
                save |= effect.etype.save_moved(effect, self)

            if not save:
                self.moved = True
            for unit in Unit.units:
                if unit.pos == pos:
                    attack, defense = self.calc_attack(unit)
                    unit.recv_damage(attack)
                    self.recv_damage(defense)
                    if unit.health <= 0 and self.utype.attack_range == 1:
                        World.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 0
                        self.pos = unit.pos
                    if unit.health <= 0:
                        for ability in self.utype.abilities:
                            Ability.get(ability).after_kill(self, unit)
                        for effect in self.effects:
                            effect.etype.after_kill(effect, self, unit)

                    for ability in self.utype.abilities:
                        Ability.get(ability).after_attack(self, unit)
                    for effect in self.effects:
                        effect.etype.after_attack(effect, self, unit)
                    break
        else:
            self.moved = True
            save = False
            for ability in self.utype.abilities:
                save |= Ability.get(ability).save_attacked(self)
            for effect in self.effects:
                save |= effect.etype.save_attacked(effect, self)
            if not save:
                self.attacked = True
            World.World.object.unit_mask[self.pos.y][self.pos.x] = 0
            self.pos = pos
            World.World.object.unit_mask[self.pos.y][self.pos.x] = 1
            for ability in self.utype.abilities:
                Ability.get(ability).after_movement(self)
            for effect in self.effects:
                effect.etype.after_movement(effect, self)
    
    def heal(self):
        heal_value = 0
        if World.World.object.get(self.pos).owner == self.owner:
            heal_value = 4
        else:
            heal_value = 2
        for ability in self.utype.abilities:
            heal_value += Ability.get(ability).additional_heal(self)
        for effect in self.effects:
            heal_value += effect.etype.additional_heal(effect, self)
        self.health = min(self.health + heal_value, self.utype.health)
        for ability in self.utype.abilities:
            Ability.get(ability).after_heal(self)
        for effect in self.effects:
            effect.etype.after_heal(effect, self)
    
    @property
    def attached_city(self) -> "City.City|None":
        if self.attached_city_id == -1:
            self._attached_city = None  
        else:
            for city in City.City.cities:
                if city._id == self.attached_city_id:
                    self._attached_city = city
                    break
        return self._attached_city

    @attached_city.setter
    def attached_city(self, city: "City.City|None"):
        self._attached_city = city
        self.attached_city_id = city._id if city is not None else -1

    def update_attached_city_id(self):
        self.attached_city_id = self._attached_city._id if self._attached_city is not None else -1

    def update_attached_city(self):
        if self.attached_city_id == -1:
            self._attached_city = None  
        else:
            for city in City.City.cities:
                if city._id == self.attached_city_id:
                    self._attached_city = city
                    break

    def get_vision_range(self) -> int:
        vision = World.World.object.get(self.pos).ttype.vision_range
        for ability in self.utype.abilities:
            vision = max(vision, Ability.get(ability).get_vision_range(self))
        for effect in self.effects:
            max(vision, effect.etype.get_vision_range(effect, self))
        return vision

    def get_visibility(self, player_id: int) -> bool:
        visibility = 1
        for ability in self.utype.abilities:
            visibility = visibility and Ability.get(ability).get_visibility(self, player_id)
        for effect in self.effects:
            visibility = visibility and effect.etype.get_visibility(effect, self, player_id)
        return visibility
    
    def end_turn(self):
        for ability in self.utype.abilities:
            Ability.get(ability).on_end_turn(self)
        for effect in self.effects:
            effect.etype.on_end_turn(effect, self)
            effect.duration -= 1
        
        i = 0
        while i < len(self.effects):
            if effect.duration <= 0:
                self.effects.remove(effect)
            else:
                i += 1 

    def validate(self, player_data: PlayerData_):
        if not player_data.joined:
            return
        player = Player.Player.by_id(player_data.id)
        return player.vision[self.pos.y][self.pos.x] and self.get_visibility(player_data.id)

    def destroy(self):
        for ability in self.utype.abilities:
            Ability.get(ability).on_death(self)
        for effect in self.effects:
            effect.etype.on_death(effect, self)
        if self.attached_city is not None:
            self.attached_city.fullness -= 1
        World.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 0
        for unit in Unit.units:
            if unit.pos == self.pos and unit != self:
                World.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = 1
                break
        Unit.units.remove(self)
        Player.Player.players[self.owner].units.remove(self)
        del self
    