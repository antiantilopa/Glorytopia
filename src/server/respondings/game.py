from serializator.host import Address, Respond
from serializator.data_format import Format
from serializator.net import flags_to_int
from server.core import *
from server.respondings.server import Server
from shared.error_codes import ErrorCodes

respond = Respond("GAME")

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
                break
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
    req_game_me_vision(self, addr, [])
    req_game_units(self, addr, new_unit_poss)
    req_game_cities(self, addr, new_city_poss)
    req_game_world(self, addr, [pos.as_tuple() for pos in changed_poss])
    

@respond.event("MOVE_UNIT")
def eve_game_mov_unit(self: Server, addr: Address, message: tuple[tuple[int, int], tuple[int, int]]):
    if addr != self.order[self.now_playing_player_index]:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"Not your move right now.")))
        return
    pos1 = message[0]
    pos2 = message[1]
    moving_unit: Unit = None
    target_unit: Unit = None
    for unit in Unit.units:
        if unit.pos.x == pos1[0] and unit.pos.y == pos1[1]:
            moving_unit = unit
        elif unit.pos.x == pos2[0] and unit.pos.y == pos2[1]:
            target_unit = unit
        if moving_unit is not None and target_unit is not None:
            break
    if moving_unit is None:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"There is no unit on the given position")))
        return
    if moving_unit.owner != self.players[addr].id:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"The unit is not yours")))
        return
    result = self.players[addr].move_unit(moving_unit, Vector2d.from_tuple(pos2))
    if result != ErrorCodes.SUCCESS:
        self.send_to_addr(addr, Format.error("GAME/MOVE_UNIT", (f"The unit cannot move to the given position")))
        return
    vision_changes = self.players[addr].update_vision()
    if len(vision_changes) != 0:
        update_vision(self, addr, vision_changes)
    if target_unit is not None:
        for player_addr in self.players:
            if self.players[player_addr].vision[pos2[1]][pos2[0]]:
                self.send_to_addr(player_addr, Format.event("GAME/UPDATE/UNIT", [pos2, target_unit.to_serializable()]))
    for player_addr in self.players:
        first = []
        second = []
        if self.players[player_addr].vision[pos1[1]][pos1[0]]:
            first = pos1
        if self.players[player_addr].vision[moving_unit.pos.y][moving_unit.pos.x]:
            second = moving_unit.to_serializable()
        if len(first) + len(second) > 0:
            self.send_to_addr(player_addr, Format.event("GAME/UPDATE/UNIT", [first, second]))
    self.the_game.remove_dead_units()
        

@respond.event("CREATE_UNIT")
def eve_game_create_unit(self: Server, addr: Address, message: tuple[tuple[int, int], int]):
    if addr == self.order[self.now_playing_player_index]:
        result = self.players[addr].create_unit(Vector2d.from_tuple(message[0]), UnitTypes.by_id(message[1]))
        if result == ErrorCodes.SUCCESS:
            unit = None
            for u in Unit.units:
                if u.pos.x == message[0][0] and u.pos.y == message[0][1]:
                    unit = u
                    break
            for player_addr in self.players:
                if self.players[player_addr].vision[unit.pos.y][unit.pos.x]:
                    self.send_to_addr(player_addr, Format.event("GAME/UPDATE/UNIT", [[], unit.to_serializable()]))
        else:
            self.send_to_addr(addr, Format.error("GAME/CREATE_UNIT", (f"Cannot create unit: {result.name}")))
    else:
        self.send_to_addr(addr, Format.error("GAME/CREATE_UNIT", (f"Not your move right now.")))

@respond.event("CONQUER_CITY")
def eve_game_conquer_city(self: Server, addr: Address, message: tuple[tuple[int, int]]):
    if addr == self.order[self.now_playing_player_index]:
        result = self.players[addr].conquer_city(Vector2d.from_tuple(message[0]))
        if result == ErrorCodes.SUCCESS:
            city = None
            for c in City.cities:
                if c.pos.x == message[0][0] and c.pos.y == message[0][1]:
                    city = c
                    break
            for player_addr in self.players:
                if self.players[player_addr].vision[city.pos.y][city.pos.x]:
                    self.send_to_addr(player_addr, Format.event("GAME/UPDATE/CITY", [city.to_serializable()]))
        else:
            self.send_to_addr(addr, Format.error("GAME/CONQUER_CITY", (f"Cannot conquer city: {result.name}")))
    else:
        self.send_to_addr(addr, Format.error("GAME/CONQUER_CITY", (f"Not your move right now.")))

@respond.event("BUY_TECH")
def eve_game_buy_tech(self: Server, addr: Address, message: tuple[int]):
    if addr == self.order[self.now_playing_player_index]:
        if message[0] < 0 or message[0] >= len(TechNode.techs):
            self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"Cannot buy tech: {ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH.name}")))
            return 
        tech = TechNode.by_id(message[0])
        result = self.players[addr].buy_tech(tech)
        if result != ErrorCodes.SUCCESS:
            self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"Cannot buy tech: {result.name}")))
        else:
            self.send_to_addr(addr, Format.event("GAME/UPDATE/TECH", [tech.id]))
    else:
        self.send_to_addr(addr, Format.error("GAME/BUY_TECH", (f"Not your move right now.")))

@respond.event("HARVEST")
def eve_game_harvest(self: Server, addr: Address, message: tuple[tuple[int, int]]):
    if addr == self.order[self.now_playing_player_index]:
        pos = Vector2d.from_tuple(message[0])
        result = self.players[addr].harvest(pos)
        if result != ErrorCodes.SUCCESS:
            self.send_to_addr(addr, Format.error("GAME/HARVEST", (f"Cannot harvest: {result.name}")))
            return
        for player_addr in self.players:
            if self.players[player_addr].vision[pos.inty()][pos.intx()]:
                self.send_to_addr(player_addr, Format.event("GAME/UPDATE/TILE", [self.the_game.world.object.get(pos).to_serializable()]))
        for city in self.players[addr].cities:
            if pos in city.domain:
                for player_addr in self.players:
                    if self.players[player_addr].vision[city.pos.y][city.pos.x]:
                        self.send_to_addr(player_addr, Format.event("GAME/UPDATE/CITY", [city.to_serializable()]))
                break
    else:
        self.send_to_addr(addr, Format.error("GAME/HARVEST", (f"Not your move right now.")))

@respond.event("BUILD")
def eve_game_build(self: Server, addr: Address, message: tuple[tuple[int, int], int]):
    if addr == self.order[self.now_playing_player_index]:
        pos = Vector2d.from_tuple(message[0])
        result = self.players[addr].build(pos, BuildingTypes.by_id(message[1]))
        if result != ErrorCodes.SUCCESS:
            self.send_to_addr(addr, Format.error("GAME/BUILD", (f"Cannot build: {result.name}")))
            return
        for player_addr in self.players:
            if self.players[player_addr].vision[pos.inty()][pos.intx()]:
                self.send_to_addr(player_addr, Format.event("GAME/UPDATE/TILE", [self.the_game.world.object.get(pos).to_serializable()]))
    else:
        self.send_to_addr(addr, Format.error("GAME/BUILD", (f"Not your move right now.")))

@respond.event("END_TURN")
def game_end_turn(self: Server, addr: Address, message: tuple):
    if addr == self.order[self.now_playing_player_index]:
        self.players[self.order[self.now_playing_player_index]].end_turn()
        self.now_playing_player_index += 1
        self.now_playing_player_index %= len(self.order)
        self.players[self.order[self.now_playing_player_index]].start_turn()
        for addr1 in self.conns:
            self.send_to_addr(addr1, Format.event("GAME/END_TURN", (self.addrs_to_names[addr])))
    else:
        self.send_to_addr(addr, Format.error("GAME/END_TURN", (f"Not your move right now.")))
