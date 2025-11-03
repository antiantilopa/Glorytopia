from netio.serialization.routing import MessageType
from server.core import *
from server.network.game_server import GameServerRouter, GamePlayer
from shared.asset_types import BuildingType, TechNode, TerraForm, UnitType
from shared.error_codes import ErrorCodes
from shared.unit import UnitData
from shared.util.position import Pos
from datetime import datetime


router = GameServerRouter("GAME")

@router.request("WORLD_SIZE")
def req_game_world_size(pdata: GamePlayer, data: tuple):
    return router.host.game.world.size.as_tuple()

@router.request("NOW_PLAYING_PLAYER_INDEX")
def get_now_playing_player_index(pdata: GamePlayer, data: tuple):
    return router.host.game.now_playing_player_index

def update_updating_objects():
    for player in Player.players:
        player.update_vision()
    router.host.create_new_objects()
    router.host.remove_dead_units()
    router.host.synchronize()

@router.event("MOVE_UNIT", datatype=tuple[Pos, Pos])
def eve_game_mov_unit(pdata: GamePlayer, data: tuple[Pos, Pos]):
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
        
@router.event("CREATE_UNIT", datatype=tuple[Pos, int])
def eve_game_create_unit(pdata: GamePlayer, data: tuple[Pos, int]):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CREATE_UNIT", (f"Not your move right now."))
        return
    pos, utype_id = data
    result = player.create_unit(pos, UnitType.by_id(utype_id))
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CREATE_UNIT", (f"Cannot create unit: {result.name}"))
        return

    update_updating_objects()

@router.event("CONQUER_CITY", datatype=Pos)
def eve_game_conquer_city(pdata: GamePlayer, pos: Pos):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CONQUER_CITY", (f"Not your move right now."))
        return
    unit = None
    for u in Unit.units:
        if u.pos == pos:
            unit = u
    city = None
    for c in City.cities:
        if c.pos == pos:
            city = c
            break
    if unit is None:
        return ErrorCodes.ERR_NOT_YOUR_UNIT
    if city is None:
        return ErrorCodes.ERR_NOT_A_CITY

    result = player.conquer_city(pos)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/CONQUER_CITY", (f"Cannot conquer city: {result.name}"))
        return
    
    update_updating_objects()
        

@router.event("BUY_TECH", datatype=int)
def eve_game_buy_tech(pdata: GamePlayer, tech_id: int):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUY_TECH", (f"Not your move right now."))
        return
    if tech_id < 0 or tech_id >= len(TechNode.values()):
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUY_TECH", (f"Cannot buy tech: {ErrorCodes.ERR_THERE_IS_NO_SUITABLE_TECH.name}"))
        return 

    tech = TechNode.by_id(tech_id)
    result = player.buy_tech(tech)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUY_TECH", (f"Cannot buy tech: {result.name}"))
        return
  
    update_updating_objects()

@router.event("HARVEST", datatype=Pos)
def eve_game_harvest(pdata: GamePlayer, pos: Pos):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/HARVEST", (f"Not your move right now."))
        return

    result = player.harvest(pos)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/HARVEST", (f"Cannot harvest: {result.name}"))
        return
    
    update_updating_objects()

@router.event("BUILD", datatype=tuple[Pos, int])
def eve_game_build(pdata: GamePlayer, data: tuple[Pos, int]):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUILD", (f"Not your move right now."))
        return

    pos, btype_id = data
    result = player.build(pos, BuildingType.by_id(btype_id))
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/BUILD", (f"Cannot build: {result.name}"))
        return
    
    update_updating_objects()

@router.event("TERRAFORM", datatype=tuple[Pos, int])
def eve_game_terraform(pdata: GamePlayer, data: tuple):
    player = Player.by_id(pdata.id)
    if pdata.id != router.host.game.now_playing_player_index:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/TERRAFORM", (f"Not your move right now."))
        return

    pos, terraform_id = data
    terraform = TerraForm.by_id(terraform_id)
    result = player.terraform(pos, terraform)
    if result != ErrorCodes.SUCCESS:
        router.host.send_message(pdata.address, MessageType.ERROR, "GAME/TERRAFORM", (f"Cannot terraform: {result.name}"))
        return
    
    update_updating_objects()

@router.event("END_TURN")
def game_end_turn(pdata: GamePlayer, data: None):
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
        router.host.send_message(pdata.address, MessageType.EVENT, "GAME/NEXT_TURN", router.host.game.now_playing_player_index)
    update_updating_objects()
