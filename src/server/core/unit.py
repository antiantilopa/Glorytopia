from netio.serialization.serializer import sync_key
from shared.asset_types import UnitType, TileType
from shared.effect import Effect, EffectType
from shared.player import SharedPlayerData
from shared.unit import UnitData
from shared.util.position import Pos
from math import floor, ceil

from . import world as world
from . import tile as tilemodule
from . import city as citymodule
from . import player as Player
from .ability import Ability

@sync_key("unit")
class Unit(UnitData):
    _attached_city: "citymodule.City|None"

    units: list["Unit"] = []

    def __init__(self, unit_type: UnitType, owner: int, pos: Pos, attached_city: "citymodule.City"):
        UnitData.__init__(self, unit_type, owner, pos)
        self.attached_city = attached_city
        Unit.units.append(self)
        world.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = self
        for ability in self.type.abilities:
            Ability.get(ability).on_spawn(self)
        for effect in self.effects:
            effect.type.on_spawn(effect, self)

    def set_pos(self, pos: Pos):
        world.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = None
        for m in world.World.object.get(self.pos).modificators:
            m.tmtype.on_unit_exit(m, world.World.object.get(self.pos), self)
        self.pos = pos
        world.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = self
        for m in world.World.object.get(self.pos).modificators:
            m.tmtype.on_unit_enter(m, world.World.object.get(self.pos), self)

    def refresh(self):
        for ability in self.type.abilities:
            Ability.get(ability).on_start_turn(self)
        for effect in self.effects:
            effect.type.on_start_turn(effect, self)
        self.moved = False
        self.attacked = False

    def get_movements(self) -> list[tuple[Pos, int|float]]:
        s_poses: list[tuple[Pos, float]] = [(self.pos, self.type.movement)]
        e_poses: list[tuple[Pos, float]] = []

        def is_in(pos: Pos, array: list[tuple[Pos, any]]) -> int:
            for poss in array:
                if poss[0] == pos:
                    return array.index(poss)
            return -1

        def get_mv(movement: float, tile: "tilemodule.Tile") -> float:
            if not self.get_stop_movement_ignore(tile):
                if tile.type.stops_movement:
                    return 0
                for ability in self.type.abilities:
                    if Ability.get(ability).stop_movement(self, tile):
                        return 0
                for effect in self.effects:
                    if effect.type.stop_movement(effect, self, tile):
                        return 0
                for m in tile.modificators:
                    if m.tmtype.stop_movement(m, tile, self):
                        return 0
            res = movement - 1 * (1 - 0.5 * tile.has_road) # legacy here btw
            for ability in self.type.abilities:
                res = max(res, Ability.get(ability).on_terrain_movement(self, tile, movement))
            for effect in self.effects:
                res = max(res, effect.type.on_terrain_movement(effect, self, tile, movement))
            for m in tile.modificators:
                res = max(res, m.tmtype.movement(m, tile, movement))
            for m in tile.modificators:
                res *= m.tmtype.bonus_movement(m, tile, movement)
            for m in tile.modificators:
                res += m.tmtype.additional_movement(m, tile, movement)
            return res
        while len(s_poses) != 0:
            s_pos = s_poses.pop(0)
            if s_pos[1] <= 0:
                if world.World.object.get_unit(s_pos[0]) is None:
                    e_poses.append(s_pos)
                continue
            for (dx, dy) in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)):
                n_pos = s_pos[0] + Pos(dx, dy)
                if not world.World.object.is_in(n_pos):
                    continue
                tmp = False
                unit = world.World.object.get_unit(n_pos)
                if unit is not None:
                    if unit.owner != self.owner:
                        tmp = True
                if tmp is True:
                    continue
                if not self.get_water_ignore(world.World.object.get(n_pos)):
                    if world.World.object.get(n_pos).type.is_water != self.type.water:
                        continue
                available = False
                for tech in Player.Player.players[self.owner].techs:
                    if world.World.object.get(n_pos).type in tech.accessable:
                        available = True
                        break
                if not available:
                    continue
                next_mv = get_mv(s_pos[1], world.World.object.get(n_pos))
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
            if world.World.object.get_unit(s_pos[0]) is None:
                e_poses.append(s_pos)
        return e_poses
    
    def get_water_ignore(self, tile: "tilemodule.Tile") -> bool:
        result = 0
        for ability in self.type.abilities:
            result += Ability.get(ability).ignore_water(self, tile)
        for effect in self.effects:
            result += effect.type.ignore_water(effect, self, tile)
        for m in tile.modificators:
            result += m.tmtype.ignore_water(m, tile, self)
        return result > 0
    
    def get_stop_movement_ignore(self, tile: "tilemodule.Tile") -> bool:
        result = 0
        for ability in self.type.abilities:
            result += Ability.get(ability).ignore_stop_movement(self, tile)
        for effect in self.effects:
            result += effect.type.ignore_stop_movement(effect, self, tile)
        for m in tile.modificators:
            result += m.tmtype.ignore_stop_movement(m, tile, self)
        return result > 0
    def get_attacks(self) -> list["Unit"]:
        result = []
        for unit in Unit.units:
            if unit.owner != self.owner:
                if max(abs((unit.pos - self.pos).x), abs((unit.pos - self.pos).y)) <= self.type.attack_range:
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
            if world.World.object.get(other.pos).type in tech.defence:
                defense_bonus = 1.5
                break
        for ability in other.type.abilities:
            defense_bonus *= Ability.get(ability).defense_bonus(other, self)
        for effect in other.effects:
            defense_bonus *= effect.type.defense_bonus(effect, other, self)

        attack_bonus = 1
        for ability in self.type.abilities:
            attack_bonus *= Ability.get(ability).attack_bonus(self, other)
        for effect in self.effects:
            attack_bonus *= effect.type.attack_bonus(effect, self, other)

        defense_value = other.type.defense
        for ability in other.type.abilities:
            defense_value += Ability.get(ability).additional_defense(other, self) 
        for effect in other.effects:
            defense_value += effect.type.additional_defense(effect, other, self) 

        attack_value = self.type.attack
        for ability in self.type.abilities:
            attack_value += Ability.get(ability).additional_attack(self, other) 
        for effect in self.effects:
            attack_value += effect.type.additional_attack(effect, self, other) 

        attack_force = attack_value * (self.health / self.type.health) * attack_bonus
        defense_force = defense_value * (other.health / other.type.health) * defense_bonus
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
                for ability in other.type.abilities:
                    defense_result = Ability.get(ability).retaliation_bonus(other, defense_result)
                for effect in other.effects:
                    defense_result = effect.type.retaliation_bonus(effect, other, defense_result)
                for ability in self.type.abilities:
                    defense_result = Ability.get(ability).retaliation_mitigate(self, defense_result)
                for effect in self.effects:
                    defense_result = effect.type.retaliation_mitigate(effect, self, defense_result)
                result[1] = defense_result
        return result
    
    def recv_damage(self, damage: int):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def move_and_attack(self, pos: Pos):
        if not (pos in self.get_possible_moves()):
            return 
        if world.World.object.get_unit(pos) is not None:
            self.attack(pos)
        else:
            self.move_to(pos)
    
    def attack(self, pos: Pos):
        if not (pos in self.get_possible_moves()):
            raise Exception("Invalid attack was given.")
        unit = world.World.object.get_unit(pos)
        if unit is None:
            raise Exception("Invalid attack was given.")
        self.attacked = True
        save = False
        for ability in self.type.abilities:
            save |= Ability.get(ability).save_moved(self)
        for effect in self.effects:
            save |= effect.type.save_moved(effect, self)

        if not save:
            self.moved = True
        attack, defense = self.calc_attack(unit)
        unit.recv_damage(attack)
        self.recv_damage(defense)
        if unit.health <= 0 and self.type.attack_range == 1:
            can_take_place = True
            if not self.get_water_ignore(world.World.object.get(unit.pos)):
                if world.World.object.get(unit.pos).type.is_water != self.type.water:
                    can_take_place = False
            available = False
            for tech in Player.Player.players[self.owner].techs:
                if world.World.object.get(unit.pos).type in tech.accessable:
                    available = True
                    break
            if can_take_place and available:
                self.set_pos(unit.pos)
        for ability in self.type.abilities:
            Ability.get(ability).after_attack(self, unit)
        for effect in self.effects:
            effect.type.after_attack(effect, self, unit)
        if unit.health <= 0:
            for ability in self.type.abilities:
                Ability.get(ability).after_kill(self, unit)
            for effect in self.effects:
                effect.type.after_kill(effect, self, unit)

    def move_to(self, pos: Pos):
        if not (pos in self.get_possible_moves()):
            raise Exception("Invalid move without attack was given.")
        if world.World.object.get_unit(pos) is not None:
            raise Exception("Invalid move without attack was given.")
        self.moved = True
        save = False
        for ability in self.type.abilities:
            save |= Ability.get(ability).save_attacked(self)
        for effect in self.effects:
            save |= effect.type.save_attacked(effect, self)
        if not save:
            self.attacked = True
        self.set_pos(pos)
        for ability in self.type.abilities:
            Ability.get(ability).after_movement(self)
        for effect in self.effects:
            effect.type.after_movement(effect, self)

    def heal(self):
        heal_value = 0
        if world.World.object.get(self.pos).owner == self.owner:
            heal_value = 4
        else:
            heal_value = 2
        for ability in self.type.abilities:
            heal_value += Ability.get(ability).additional_heal(self)
        for effect in self.effects:
            heal_value += effect.type.additional_heal(effect, self)
        self.health = min(self.health + heal_value, self.type.health)
        for ability in self.type.abilities:
            Ability.get(ability).after_heal(self)
        for effect in self.effects:
            effect.type.after_heal(effect, self)
    
    def act(self, action_id: int):
        for effect in self.effects:
            if action_id in effect.type.actions:
                effect.type.actions[action_id](effect, self)
        for ability_name in self.type.abilities:
            ability = Ability.get(ability_name)
            if action_id in ability.actions:
                ability.actions[action_id](self)
                
    @property
    def attached_city(self) -> "citymodule.City|None":
        if self.attached_city_id == -1:
            self._attached_city = None  
        else:
            for city in citymodule.City.cities:
                if city._id == self.attached_city_id:
                    self._attached_city = city
                    break
        return self._attached_city

    @attached_city.setter
    def attached_city(self, city: "citymodule.City|None"):
        self._attached_city = city
        self.attached_city_id = city._id if city is not None else -1

    def update_attached_city_id(self):
        self.attached_city_id = self._attached_city._id if self._attached_city is not None else -1

    def update_attached_city(self):
        if self.attached_city_id == -1:
            self._attached_city = None  
        else:
            for city in citymodule.City.cities:
                if city._id == self.attached_city_id:
                    self._attached_city = city
                    break

    def get_vision_range(self) -> int:
        vision = world.World.object.get(self.pos).type.vision_range
        for ability in self.type.abilities:
            vision = max(vision, Ability.get(ability).get_vision_range(self))
        for effect in self.effects:
            vision = max(vision, effect.type.get_vision_range(effect, self))
        return vision

    def get_visibility(self, player_id: int) -> bool:
        visibility = 1
        for ability in self.type.abilities:
            visibility = visibility and Ability.get(ability).get_visibility(self, player_id)
        for effect in self.effects:
            visibility = visibility and effect.type.get_visibility(effect, self, player_id)
        return visibility
    
    def update_effects(self):
        i = 0
        while i < len(self.effects):
            if self.effects[i].duration == 0:
                self.effects.pop(i)
            else:
                i += 1 

    def end_turn(self):
        for ability in self.type.abilities:
            Ability.get(ability).on_end_turn(self)
        for effect in self.effects:
            effect.type.on_end_turn(effect, self)
            if effect.duration > 0:
                effect.duration -= 1
        self.update_effects()

    def validate(self, player_data: SharedPlayerData):
        if not player_data.joined:
            return False
        player = Player.Player.by_id(player_data.id)
        if player.is_dead:
            return True
        return player.vision[self.pos.y][self.pos.x] and self.get_visibility(player_data.id)

    def destroy(self):
        for ability in self.type.abilities:
            Ability.get(ability).on_death(self)
        for effect in self.effects:
            effect.type.on_death(effect, self)
        if self.attached_city is not None:
            self.attached_city.fullness -= 1
        world.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = None
        for unit in Unit.units:
            if unit.pos == self.pos and unit != self:
                world.World.object.unit_mask[self.pos.inty()][self.pos.intx()] = unit
                print("\n\n\n\n(!!!) SOME BULLSHIT JUST HAPPENED? THIS IS JUST BULLSHIT CODE\n\n")
                break
        Unit.units.remove(self)
        Player.Player.players[self.owner].units.remove(self)
        del self
    