from serializator.host import Address, Respond
from serializator.data_format import Format
from serializator.net import flags_to_int
from server.core import *
from server.network.server import Server
from shared.asset_types import BuildingType, TechNode, TerraForm, UnitType
from shared.error_codes import ErrorCodes
from shared.unit import UnitData
from engine_antiantilopa import Vector2d
from datetime import datetime


respond = Respond("GAME")

@respond.request("WORLD_SIZE")
def req_game_world_size(self: Server, addr: Address, message: tuple):
    self.send_to_addr(addr, Format.info("GAME/WORLD_SIZE", (self.the_game.world.size.as_tuple())))

@respond.request("NOW_PLAYING_PLAYER_INDEX")
def get_now_playing_player_index(self: Server, addr: Address, message: tuple):
    self.send_to_addr(addr, Format.info("GAME/NOW_PLAYING_PLAYER_INDEX", [self.the_game.now_playing_player_index]))

@respond.request("WORLD")
def req_game_world(self: Server, addr: Address, message: list[tuple[int, int]]):
    if len(message) != 0:
        result = []
        for pos in message:
            if self.players[addr].vision[pos[1]][pos[0]]:
                result.append(self.the_game.world.get(Vector2d(pos[0], pos[1])).to_serializable())
    else:
        result = []
        for i in range(self.the_game.world.size.x):
            for j in range(self.the_game.world.size.y):
                if self.players[addr].vision[j][i]:
                    result.append(self.the_game.world[j][i].to_serializable())
    self.send_to_addr(addr, Format.info("GAME/WORLD", result))

def update_unit(self: Server, unit: Unit, previous_pos: Vector2d = None):
    if previous_pos is None:
        previous_pos = unit.previous_pos
    for player_addr in self.players:
        last = ()
        prev = ()
        if self.players[player_addr].vision[unit.pos.y][unit.pos.x]:
            last = UnitData.to_serializable(unit)
        if unit.previous_pos == Vector2d(-1, -1):
            prev = ()
        elif self.players[player_addr].vision[previous_pos.y][previous_pos.x]:
            prev = previous_pos.as_tuple()
        if len(last) + len(prev) == 0:
            continue
        self.send_to_addr(player_addr, Format.event("GAME/UPDATE/UNIT", [prev, last]))
    unit.refresh_updated()

def update_city(self: Server, city: City):
    for player_addr in self.players:
        if city is not None and self.players[player_addr].vision[city.pos.y][city.pos.x]:
            self.send_to_addr(player_addr, Format.event("GAME/UPDATE/CITY", [city.to_serializable()]))
    city.refresh_updated()

def update_tile(self: Server, tile: Tile):
    for player_addr in self.players:
        if tile is not None and self.players[player_addr].vision[tile.pos.y][tile.pos.x]:
            self.send_to_addr(player_addr, Format.event("GAME/UPDATE/TILE", [tile.to_serializable()]))
    tile.refresh_updated()

def update_player(self: Server, player_addr: Address):
    if self.players[player_addr].updated:
        self.send_to_addr(player_addr, Format.event("GAME/UPDATE/TECH", [tech.id for tech in self.players[player_addr].techs]))
        self.send_to_addr(player_addr, Format.event("GAME/UPDATE/MONEY", [self.players[player_addr].money]))
    vision_changes = self.players[player_addr].update_vision()
    if len(vision_changes) != 0:
        update_vision(self, player_addr, vision_changes)
    self.players[player_addr].refresh_updated()

def update_updating_objects(self: Server):
    for unit in Unit.units:
        if unit.health <= 0:
            update_unit(self, unit)
    for unit in Unit.units:
        if unit.updated and unit.health > 0:
            update_unit(self, unit)
    for i in range(World.object.size.y):
        for j in range(World.object.size.x):
            tile = World.object.get(Vector2d(j, i))
            if tile.updated:
                update_tile(self, tile)
    for city in City.cities:
        if city.updated:
            update_city(self, city)

    for addr in self.players:
        update_player(self, addr)
    
    self.the_game.remove_dead_units()
    
@respond.request("UNITS")
def req_game_units(self: Server, addr: Address, message: list[tuple[int, int]]):
    if len(message) != 0:
        result = []
        for unit in Unit.units:
            if self.players[addr].vision[unit.pos.y][unit.pos.x]:
                if (unit.pos.x, unit.pos.y in message):
                    result.append(unit.to_serializable())
    else:
        result = []
        for unit in Unit.units:
            if self.players[addr].vision[unit.pos.y][unit.pos.x]:
                result.append(unit.to_serializable())
    self.send_to_addr(addr, Format.info("GAME/UNITS", result))

@respond.request("CITIES")
def req_game_cities(self: Server, addr: Address, message: list[tuple[int, int]]):
    if len(message) != 0:
        result = []
        for city in City.cities:
            if self.players[addr].vision[city.pos.y][city.pos.x]:
                for pos in message:
                    if city.pos.x == pos[0] and city.pos.y == pos[1]:
                        result.append(city.to_serializable())
                        break
    else:
        result = []
        for city in City.cities:
            if self.players[addr].vision[city.pos.y][city.pos.x]:
                result.append(city.to_serializable())
    self.send_to_addr(addr, Format.info("GAME/CITIES", result))

@respond.request("MY_TECHS")
def req_game_me_techs(self: Server, addr: Address, message: tuple):
    result = [tech.id for tech in self.players[addr].techs]
    self.send_to_addr(addr, Format.info("GAME/MY_TECHS", result))

@respond.request("MY_CITIES")
def req_game_me_cities(self: Server, addr: Address, message: tuple):
    result = [city.to_serializable() for city in self.players[addr].cities]
    self.send_to_addr(addr, Format.info("GAME/MY_CITIES", result))

@respond.request("MY_UNITS")
def req_game_me_units(self: Server, addr: Address, message: tuple):
    result = [unit.to_serializable() for unit in self.players[addr].units]
    self.send_to_addr(addr, Format.info("GAME/MY_UNITS", result))

@respond.request("MY_VISION")
def req_game_me_vision(self: Server, addr: Address, message: tuple[None]):
    result = []
    for row in self.players[addr].vision:
        result.append(flags_to_int(*row))
    self.send_to_addr(addr, Format.info("GAME/MY_VISION", result))

@respond.request("MY_MONEY")
def req_game_me_cities(self: Server, addr: Address, message: tuple):
    result = [self.players[addr].money]
    self.send_to_addr(addr, Format.info("GAME/MY_MONEY", result))

def update_vision(self: Server, addr: Address, changed_poss: list[Vector2d]):
    new_unit_poss = []
    new_city_poss = []
    for pos in changed_poss:
        for unit in Unit.units:
            if unit.pos == pos:
                new_unit_poss.append(unit.pos.as_tuple())
                break
        for city in City.cities:
            if city.pos == pos:
                new_city_poss.append(city.pos.as_tuple())
                break
    for unit in Unit.units:
        if unit.pos in changed_poss:   
            self.send_to_addr(addr, Format.event("GAME/UPDATE/UNIT", [(), unit.to_serializable()]))
    for city in City.cities:
        if city.pos in changed_poss:
            self.send_to_addr(addr, Format.event("GAME/UPDATE/CITY", [city.to_serializable()]))
    for pos in changed_poss:
        self.send_to_addr(addr, Format.event("GAME/UPDATE/TILE", [self.the_game.world.get(pos).to_serializable()]))

@respond.event("MOVE_UNIT")
def eve_game_mov_unit(self: Server, addr: Address, message: tuple[tuple[int, int], tuple[int, int]]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"Not your move right now.")))
        return
    if World.object.unit_mask[message[0][1]][message[0][0]] == 0:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"There is no unit on the given position")))
        return

    pos1 = message[0]
    pos2 = message[1]
    moving_unit: Unit = None
    for unit in Unit.units:
        if unit.pos.x == pos1[0] and unit.pos.y == pos1[1]:
            moving_unit = unit
            break

    result = self.players[addr].move_unit(moving_unit, Vector2d.from_tuple(pos2))
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"Cannot move unit: {result.name}")))
        return

    update_updating_objects(self)
        
@respond.event("CREATE_UNIT")
def eve_game_create_unit(self: Server, addr: Address, message: tuple[tuple[int, int], int]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/CREATE_UNIT", (f"Not your move right now.")))
        return
    result = self.players[addr].create_unit(Vector2d.from_tuple(message[0]), UnitType.by_id(message[1]))
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/CREATE_UNIT", (f"Cannot create unit: {result.name}")))
        return

    update_updating_objects(self)

@respond.event("CONQUER_CITY")
def eve_game_conquer_city(self: Server, addr: Address, message: tuple[tuple[int, int]]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/CONQUER_CITY", (f"Not your move right now.")))
        return
    unit = None
    for u in Unit.units:
        if u.pos.x == message[0][0] and u.pos.y == message[0][1]:
            unit = u
    city = None
    for c in City.cities:
        if c.pos.x == message[0][0] and c.pos.y == message[0][1]:
            city = c
            break
    if unit is None:
        return ErrorCodes.ERR_NOT_YOUR_UNIT
    if city is None:
        return ErrorCodes.ERR_NOT_A_CITY
    
    result = self.players[addr].conquer_city(Vector2d.from_tuple(message[0]))
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/CONQUER_CITY", (f"Cannot conquer city: {result.name}")))
        return
    
    update_updating_objects(self)
        

@respond.event("BUY_TECH")
def eve_game_buy_tech(self: Server, addr: Address, message: tuple[int]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"Not your move right now.")))
        return
    if addr not in self.order:
        self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"You are not playing.")))
        return
    if message[0] < 0 or message[0] >= len(TechNode.values()):
        self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"Cannot buy tech: {ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH.name}")))
        return 
    tech = TechNode.by_id(message[0])
    result = self.players[addr].buy_tech(tech)
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"Cannot buy tech: {result.name}")))
        return
  
    update_updating_objects(self)

@respond.event("HARVEST")
def eve_game_harvest(self: Server, addr: Address, message: tuple[tuple[int, int]]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/HARVEST", (f"Not your move right now.")))
        return
    pos = Vector2d.from_tuple(message[0])
    result = self.players[addr].harvest(pos)
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/HARVEST", (f"Cannot harvest: {result.name}")))
        return
    
    update_updating_objects(self)

@respond.event("BUILD")
def eve_game_build(self: Server, addr: Address, message: tuple[tuple[int, int], int]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/BUILD", (f"Not your move right now.")))
        return
    pos = Vector2d.from_tuple(message[0])
    result = self.players[addr].build(pos, BuildingType.by_id(message[1]))
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/BUILD", (f"Cannot build: {result.name}")))
        return
    
    update_updating_objects(self)

@respond.event("TERRAFORM")
def eve_game_terraform(self: Server, addr: Address, message: tuple[tuple[int, int], int]):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/TERRAFORM", (f"Not your move right now.")))
        return
    pos = Vector2d.from_tuple(message[0])
    terraform = TerraForm.by_id(message[1])
    result = self.players[addr].terraform(pos, terraform)
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/TERRAFORM", (f"Cannot terraform: {result.name}")))
        return
    
    update_updating_objects(self)

@respond.event("END_TURN")
def game_end_turn(self: Server, addr: Address, message: tuple):
    if addr != self.order[self.the_game.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/END_TURN", (f"Not your move right now.")))
        return

    dead = []
    for addr in self.players:
        if self.players[addr].is_dead:
            dead.append(addr)

    self.the_game.next_player_turn()

    for addr in self.players:
        if self.players[addr].is_dead:
            if addr in dead:
                continue
            else:
                for addr1 in self.conns:
                    self.send_to_addr(addr1, Format.event("GAME/GAME_OVER", [self.addrs_to_names[addr]]))
                req_game_world(self, self.order.index(addr), [])
                req_game_cities(self, self.order.index(addr), [])
                req_game_units(self, self.order.index(addr), [])

    for addr1 in self.conns:
        self.send_to_addr(addr1, Format.event("GAME/END_TURN", [self.the_game.now_playing_player_index]))

    update_updating_objects(self)
