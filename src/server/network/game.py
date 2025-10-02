from netio.serialization.routing import MessageType
from server.core import *
from server.network.game_server import GameServerRouter
from shared.asset_types import BuildingType, TechNode, TerraForm, UnitType
from shared.error_codes import ErrorCodes
from shared.unit import UnitData
from engine_antiantilopa import Vector2d
from datetime import datetime
from shared.player import PlayerData_


router = GameServerRouter("GAME")

@router.request("WORLD_SIZE")
def req_game_world_size(pdata: PlayerData_, data: tuple):
    return router.host.game.world.size.as_tuple()

@router.request("NOW_PLAYING_PLAYER_INDEX")
def get_now_playing_player_index(pdata: PlayerData_, data: tuple):
    return router.host.game.now_playing_player_index

@router.request("WORLD")
def req_game_world(pdata: PlayerData_, data: tuple[Vector2d]):
    player = Player.by_id(pdata.id)
    if len(data) != 0:
        result = []
        for pos in data:
            if player.vision[pos.inty()][pos.intx()]:
                result.append(router.host.game.world.get(Vector2d(pos[0], pos[1])))
    else:
        result = []
        for i in range(router.host.game.world.size.x):
            for j in range(router.host.game.world.size.y):
                if player.vision[j][i]:
                    result.append(router.host.game.world[j][i])
    return result
    
@router.request("UNITS")
def req_game_units(pdata: PlayerData_, data: tuple[Vector2d]):
    player = Player.by_id(pdata.id)
    if len(data) != 0:
        result = []
        for unit in Unit.units:
            if player.vision[unit.pos.y][unit.pos.x]:
                if (unit.pos in data):
                    result.append(unit)
    else:
        result = []
        for unit in Unit.units:
            if player.vision[unit.pos.y][unit.pos.x]:
                result.append(unit)
    return result

@router.request("CITIES")
def req_game_cities(pdata: PlayerData_, data: tuple[Vector2d]):
    player = Player.by_id(pdata.id)
    if len(data) != 0:
        result = []
        for city in City.cities:
            if player.vision[city.pos.y][city.pos.x]:
                if (city.pos in data):
                    result.append(city)
    else:
        result = []
        for city in City.cities:
            if player.vision[city.pos.y][city.pos.x]:
                result.append(city)
    return result

@router.request("MY_TECHS")
def req_game_my_techs(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    result = [tech for tech in player.techs]
    return result

@router.request("MY_CITIES")
def req_game_me_cities(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    result = [city for city in player.cities]
    return result

@router.request("MY_UNITS")
def req_game_me_units(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    result = [unit for unit in player.units]
    return result

@router.request("MY_VISION")
def req_game_me_vision(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    return player.vision

@router.request("MY_MONEY")
def req_game_me_cities(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    return player.money

def update_updating_objects():
    router.host.synchronize()
    router.host.remove_dead_units()



@router.event("MOVE_UNIT")
def eve_game_mov_unit(pdata: PlayerData_, data: tuple[Vector2d, Vector2d]):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/MOVE_UNIT", f"Not your move right now.")
        return
    if World.object.unit_mask[data[0].inty()][data[0].intx()] == 0:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/MOVE_UNIT", f"There is no unit on the given position")
        return

    pos1 = data[0]
    pos2 = data[1]
    moving_unit: Unit = None
    for unit in Unit.units:
        if unit.pos == pos1:
            moving_unit = unit
            break

    result = player.move_unit(moving_unit, pos2)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/MOVE_UNIT", f"Cannot move unit: {result.name}")
        return

    update_updating_objects()
        
@router.event("CREATE_UNIT")
def eve_game_create_unit(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CREATE_UNIT", (f"Not your move right now."))
        return

    result = player.create_unit(Vector2d.from_tuple(data[0]), UnitType.by_id(data[1]))
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CREATE_UNIT", (f"Cannot create unit: {result.name}"))
        return

    update_updating_objects()

@router.event("CONQUER_CITY")
def eve_game_conquer_city(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CONQUER_CITY", (f"Not your move right now."))
        return
    unit = None
    for u in Unit.units:
        if u.pos.x == data[0][0] and u.pos.y == data[0][1]:
            unit = u
    city = None
    for c in City.cities:
        if c.pos.x == data[0][0] and c.pos.y == data[0][1]:
            city = c
            break
    if unit is None:
        return ErrorCodes.ERR_NOT_YOUR_UNIT
    if city is None:
        return ErrorCodes.ERR_NOT_A_CITY

    result = player.conquer_city(Vector2d.from_tuple(data[0]))
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CONQUER_CITY", (f"Cannot conquer city: {result.name}"))
        return
    
    update_updating_objects()
        

@router.event("BUY_TECH")
def eve_game_buy_tech(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUY_TECH", (f"Not your move right now."))
        return
    if data[0] < 0 or data[0] >= len(TechNode.values()):
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUY_TECH", (f"Cannot buy tech: {ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH.name}"))
        return 

    tech = TechNode.by_id(data[0])
    result = player.buy_tech(tech)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUY_TECH", (f"Cannot buy tech: {result.name}"))
        return
  
    update_updating_objects()

@router.event("HARVEST")
def eve_game_harvest(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/HARVEST", (f"Not your move right now."))
        return

    pos = Vector2d.from_tuple(data[0])
    result = player.harvest(pos)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/HARVEST", (f"Cannot harvest: {result.name}"))
        return
    
    update_updating_objects()

@router.event("BUILD")
def eve_game_build(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUILD", (f"Not your move right now."))
        return

    pos = Vector2d.from_tuple(data[0])
    result = player.build(pos, BuildingType.by_id(data[1]))
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUILD", (f"Cannot build: {result.name}"))
        return
    
    update_updating_objects()

@router.event("TERRAFORM")
def eve_game_terraform(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/TERRAFORM", (f"Not your move right now."))
        return

    pos = Vector2d.from_tuple(data[0])
    terraform = TerraForm.by_id(data[1])
    result = player.terraform(pos, terraform)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/TERRAFORM", (f"Cannot terraform: {result.name}"))
        return
    
    update_updating_objects()

@router.event("END_TURN")
def game_end_turn(pdata: PlayerData_, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/END_TURN", (f"Not your move right now."))
        return

    dead = []
    for player in Player.players:
        if player.is_dead:
            dead.append(player)

    router.host.game.next_player_turn()
    
    for player in Player.players:
        if player.is_dead:
            if player in dead:
                continue
            else:
                for others in Player.players:
                    router.host.send_message(others.pdata.address, MessageType.EVENT, "GAME/GAME_OVER", player.pdata.nickname)

    for player in Player.players:
        router.host.send_message(pdata.address, MessageType.EVENT, "GAME/GAME_OVER", router.host.game.now_playing_player_index)
    update_updating_objects()
