from server.core.player import Player
from server.network.game_server import GameServer, GameServerRouter, GamePlayer
from netio.serialization.routing import MessageType
from shared.asset_types import Nation

router = GameServerRouter("LOBBY")

@router.request("JOIN", datatype=str)
def join(pdata: GamePlayer, data: str):
    if router.host.game_started:
        if any(p.nickname == data for p in GamePlayer.need_reconnect):
            pdata.nickname = data
            return 1
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "This game has already started.")
        return -1
    name = data
    if pdata.id != -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "You have already joined the lobby.")
        return -1
    if name in [i.nickname for i in router.host.game_manager.players]:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "This name is already taken.")
        return -1
    if name == "":
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "Name cannot be empty.")
        return -1
    if not (name.isascii()):
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "This name contains non-ascii characters.")
        return -1
    if len(name) > 15:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", f"This name is too long: {len(name)}. 15 symbols maximum.")
        return -1
    for prohibited_name in router.host.prohibited_names:
        if prohibited_name in name.lower():
            router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", f"This name contains prohibited substring: {prohibited_name}.")
            return -1

    print(f"{name} joined the game!")

    used_colors = list(dict.fromkeys([player.color for player in GamePlayer.joined_players]))
    
    def mex(ordered_list: list[int]) -> int:
        l = 0 
        r = len(ordered_list) - 1
        while l <= r:
            mid = (l + r) // 2
            if ordered_list[mid] != mid and (mid == 0 or ordered_list[mid - 1] == mid - 1):
                return mid
            elif ordered_list[mid] != mid:
                r = mid - 1
            else:
                l = mid + 1
        return len(ordered_list)
    
    pdata.color = mex(used_colors)
    pdata.nation = Nation.by_id(0)
    pdata.id = max([-1] + [player.id for player in GamePlayer.joined_players]) + 1
    pdata.nickname = name

    pdata.joined = 1
    GamePlayer.joined_players.append(pdata)
    router.host.synchronize()

    for player in GamePlayer.joined_players:
        router.host.send_message(player.address, MessageType.EVENT, "LOBBY/JOIN", None)

    return 0

@router.request("RECONNECT", datatype=int)
def reconnect(pdata: GamePlayer, data: int):
    if not router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", "this game has not started yet.")
        return -1
    if pdata in GamePlayer.joined_players:
        router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", "you are already connected.")
        return -1
    name = pdata.nickname
    recovery_code = data
    if name not in [pdata.nickname for pdata in GamePlayer.need_reconnect]:
        router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", ["you are not registered in this game."])
        return -1
    savedata = [sdata for sdata in GamePlayer.need_reconnect if sdata.nickname == name][0]
    if savedata.recovery_code != recovery_code:
        router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", ["recovery code is not correct."])
        return -1
    
    pdata.recovery_code = None
    pdata.copy_from(savedata)

    GamePlayer.joined_players.append(pdata)
    Player.by_id(pdata.id).pdata = pdata
    router.host.synchronize()
    pdata.joined = 1
    
    router.host.send_message(pdata.address, MessageType.EVENT, "LOBBY/RECONNECT", (router.host.game.now_playing_player_index, router.host.game.world.size))

    for j in GamePlayer.joined_players:
        router.host.send_message(j.address, MessageType.EVENT, "GAME/RECONNECT", pdata.nickname)
    
    return 0

@router.event("MESSAGE", datatype=str)
def message_event(pdata: GamePlayer, data: str):
    message = data
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if message == "":
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "message cannot be empty.")
        return
    if not message.isascii():
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "this message contains non-ascii characters.")
        return
    if message.isspace():
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "message cannot be only spaces.")
        return
    if len(message) > 50:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "message is too long. 50 characters maximum.")
        return
    
    print(f"<{pdata.nickname}> {message[0]}")
    for pdata2 in GamePlayer.joined_players:
        router.host.send_message(pdata2.address, MessageType.EVENT, "LOBBY/MESSAGE", (pdata.nickname, message))

@router.event("READY", datatype=int)
def ready(pdata: GamePlayer, data: bool):
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/READY", "this game has already started.")
        return
    is_ready = bool(data)
    if is_ready:
        print(f"! <{pdata.nickname}> ready")
    else:
        print(f"! <{pdata.nickname}> not ready")
    pdata.is_ready = is_ready

    router.host.synchronize()

    for pdata2 in GamePlayer.joined_players:
        router.host.send_message(pdata2.address, MessageType.EVENT, "LOBBY/READY", None)

    if is_ready:
        if all([i.is_ready for i in GamePlayer.joined_players]):
            router.host.game_starting = True
    else:
        router.host.game_starting = False

@router.event("COLOR_CHANGE", datatype=int)
def color_change(pdata: GamePlayer, data: int):
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/READY", "this game has already started.")
        return
    color = int(data)
    if color in [i.color for i in GamePlayer.joined_players]:
        router.host.game_manager.send_error(pdata.address, "LOBBY/COLOR_CHANGE", f"this color {color} is already taken.")
        return
    if color < 0:
        router.host.game_manager.send_error(pdata.address, "LOBBY/COLOR_CHANGE", f"this color {color} is out of range. [0; +inf) are allowed.")
        return

    pdata.color = color
    router.host.synchronize()
    for i in GamePlayer.joined_players:
        router.host.send_message(i.address, MessageType.EVENT, "LOBBY/COLOR_CHANGE", None)

@router.event("NATION_CHANGE", datatype=int)
def nation_change(pdata: GamePlayer, data: int):
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/READY", "this game has already started.")
        return
    nation_id = int(data)
    if not (0 <= nation_id < len(Nation.values())):
        router.host.game_manager.send_error(pdata.address, "LOBBY/NATION_CHANGE", [f"this nation {nation_id} is out of range. [0; {len(Nation.values())}) are allowed."])
        return
    
    nation = Nation.by_id(nation_id)

    pdata.nation = nation

    router.host.synchronize()


@router.event("ADMIN/CHANGE_ORDER", datatype=tuple[int, int])
def eve_lobby_change_order(pdata: GamePlayer, data: tuple[int, int]):
    raise NotImplementedError("ADMIN/CHANGE_ORDER")