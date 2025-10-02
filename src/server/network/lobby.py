from server.network.game_server import GameServerRouter
from netio.serialization.routing import MessageType
from shared.asset_types import Nation
from shared.player import PlayerData_

router = GameServerRouter("LOBBY")

@router.event("JOIN")
def join(pdata: PlayerData_, data: tuple[str]):
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "This game has already started.")
        return
    name = data[0]
    if pdata.id != -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "You have already joined the lobby.")
        return
    if name in [i.nickname for i in router.host.game_manager.players]:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "This name is already taken.")
        return
    if name == "":
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "Name cannot be empty.")
        return
    if not (name.isascii()):
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", "This name contains non-ascii characters.")
        return
    if len(name) > 15:
        router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", f"This name is too long: {len(name)}. 15 symbols maximum.")
        return
    for prohibited_name in router.host.prohibited_names:
        if prohibited_name in name.lower():
            router.host.game_manager.send_error(pdata.address, "LOBBY/JOIN", f"This name contains prohibited substring: {prohibited_name}.")
            return

    print(f"{name[0]} joined the game!")

    used_colors = list(dict.fromkeys([player.color for player in router.host.game_manager.players]))
    
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
    pdata.id = max([-1] + [player.id for player in router.host.game_manager.players]) + 1
    pdata.is_dead = False
    pdata.nickname = name

    for pdata2 in router.host.game_manager.players:
        router.host.send_message(pdata2.address, MessageType.EVENT, "LOBBY/JOIN", (name, pdata.color, pdata.nation))

# TODO !!! SAVE PLAYER DATA NOT DONE YET !!!

# @router.event("RECONNECT")
# def reconnect(pdata: PlayerData_, data: tuple):
#     if not self.game_started:
#         router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", ["this game has not started yet."]))
#         return
#     if addr in [pdata.addr for pdata in router.host.game_manager.players]:
#         router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", ["you are already connected."]))
#         return
#     name, recovery_code = name_and_recovery
#     if name not in [pdata.nickname for pdata in router.host.game_manager.players]:
#         router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", ["you are not registered in this game."]))
#         return
#     pdata = Connection.get_by_name(name)
#     if pdata.recovery_code != recovery_code:
#         router.host.game_manager.send_error(pdata.address, "LOBBY/RECONNECT", ["recovery code is not correct."]))
#         return
    
#     pdata.recovery_code = None
#     pdata.addr = addr
#     pdata.pdata = router.host.game_manager.players[addr]
    
#     for j in router.host.game_manager.players:
#         self.send_to_addr(j, Format.event("LOBBY/RECONNECT", [pdata.nickname]))

@router.event("MESSAGE")
def message_event(pdata: PlayerData_, data: tuple[str]):
    message = data[0]
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
    for pdata2 in router.host.game_manager.players:
        router.host.send_message(pdata2.address, MessageType.EVENT, "LOBBY/MESSAGE", (pdata.nickname, message))

@router.event("READY")
def ready(pdata: PlayerData_, data: tuple[bool]):
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/READY", "this game has already started.")
        return
    if data[0]:
        print(f"! <{pdata.nickname}> ready")
    else:
        print(f"! <{pdata.nickname}> not ready")
    pdata.is_ready = bool(data[0])
    for pdata2 in router.host.game_manager.players:
        router.host.send_message(pdata2.address, MessageType.EVENT, "LOBBY/READY", (pdata.nickname, pdata.is_ready))

    if data[0]:
        start = True
        for ready in [i.is_ready for i in router.host.game_manager.players]:
            start = start and ready
        if start:
            router.host.game_starting = True
            return
    else:
        router.host.game_starting = False

@router.event("COLOR_CHANGE")
def color_change(pdata: PlayerData_, data: tuple[int]):
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/READY", "this game has already started.")
        return
    color = int(data[0])
    if color in [i.color for i in router.host.game_manager.players]:
        router.host.game_manager.send_error(pdata.address, "LOBBY/COLOR_CHANGE", f"this color {color} is already taken.")
        return
    if color < 0:
        router.host.game_manager.send_error(pdata.address, "LOBBY/COLOR_CHANGE", f"this color {color} is out of range. [0; +inf) are allowed.")
        return

    pdata.color = color
    for i in router.host.game_manager.players:
        router.host.send_message(i.address, MessageType.EVENT, "LOBBY/COLOR_CHANGE", (pdata.nickname, color))

@router.event("NATION_CHANGE")
def nation_change(pdata: PlayerData_, data: tuple[int]):
    if pdata.id == -1:
        router.host.game_manager.send_error(pdata.address, "LOBBY/MESSAGE", "you did not joined the lobby.")
        return
    if router.host.game_started:
        router.host.game_manager.send_error(pdata.address, "LOBBY/READY", "this game has already started.")
        return
    if not (0 <= int(data[0]) < len(Nation.values())):
        router.host.game_manager.send_error(pdata.address, "LOBBY/NATION_CHANGE", [f"this nation {int(data[0])} is out of range. [0; {len(Nation.values())}) are allowed."])
        return
    
    nation = Nation.by_id(int(data[0]))

    pdata.nation = nation

@router.event("ADMIN/CHANGE_ORDER")
def eve_lobby_change_order(pdata: PlayerData_, data: tuple):
    raise NotImplementedError("ADMIN/CHANGE_ORDER")

@router.request("READINESS")
def req_readiness(pdata: PlayerData_, data: tuple):
    return [(pdata.nickname, pdata.is_ready) for pdata in router.host.game_manager.players]

@router.request("NAMES")
def req_readiness(pdata: PlayerData_, data: tuple):
    return[pdata.nickname for pdata in router.host.game_manager.players]

@router.request("COLORS")
def req_color(pdata: PlayerData_, data: tuple):
    return[(pdata.nickname, pdata.color) for pdata in router.host.game_manager.players]

@router.request("NATIONS")
def req_color(pdata: PlayerData_, data: tuple):
    return[(pdata.nickname, pdata.color) for pdata in router.host.game_manager.players]