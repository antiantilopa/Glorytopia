from netio.router import ServerRouter
from netio.serialization.routing import MessageType
from shared.asset_types import Nation
from shared.player import PlayerData

router = ServerRouter("LOBBY")

@router.event("JOIN")
def join(player_data: PlayerData, name: tuple[str]):
    if router.host.game_started:
        router.host.game_manager.send_error(player_data.address, "", "This game has already started.")
        return
    if (name[0] in [i.nickname for i in router.host.game_manager.players]) or (name[0] == "") or not (name[0].isascii()):
        router.host.game_manager.send_error(player_data.address, "", "This name is already taken, or it is prohibited.")
        return
    if len(name[0]) > 15:
        router.host.game_manager.send_error(player_data.address, "", "This name is too long. 15 symbols maximum.")
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

    new_conn = Connection(addr, name[0], self.conns[addr])
    new_conn.color = mex(used_colors)

    self.game_starting = False
    for j in self.conns:
        self.send_to_addr(j, Format.event("LOBBY/JOIN", [new_conn.name]))
        self.send_to_addr(j, Format.event("LOBBY/COLOR_CHANGE", (new_conn.name, new_conn.color)))

@respond.event("RECONNECT")
def reconnect(self: Server, addr: Address, name_and_recovery: tuple[str, int]):
    if not self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["this game has not started yet."]))
        return
    if addr in [conn.addr for conn in Connection.conns]:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["you are already connected."]))
        return
    name, recovery_code = name_and_recovery
    if name not in [conn.name for conn in Connection.conns]:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["you are not registered in this game."]))
        return
    conn = Connection.get_by_name(name)
    if conn.recovery_code != recovery_code:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["recovery code is not correct."]))
        return
    
    conn.recovery_code = None
    conn.addr = addr
    conn.conn = self.conns[addr]
    
    for j in self.conns:
        self.send_to_addr(j, Format.event("LOBBY/RECONNECT", [conn.name]))

@respond.event("MESSAGE")
def message(self: Server, addr: Address, message: tuple[str]):
    if message[0] == "":
        self.send_to_addr(addr, Format.error("LOBBY/MESSAGE", ["message cannot be empty."]))
        return
    if len(message[0]) > 50:
        self.send_to_addr(addr, Format.error("LOBBY/MESSAGE", ["message is too long. 64 characters maximum."]))
        return
    conn = Connection.get_by_addr(addr)
    print(f"<{conn.name}> {message[0]}")
    for i in self.conns:
        self.send_to_addr(i, Format.event("LOBBY/MESSAGE", (conn.name, message[0])))

@respond.event("READY")
def ready(self: Server, addr: Address, player_readiness: tuple[int]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/READY", ["this game has already started."]))
        return
    if addr not in [i.addr for i in Connection.conns]:
        self.send_to_addr(addr, Format.error("LOBBY/READY", ["you did not joined the lobby."]))
        return
    conn = Connection.get_by_addr(addr)
    print(f"! <{conn.name}> ready = {(player_readiness[0])}")
    conn.ready = int(bool(player_readiness[0]))
    for i in self.conns:
        self.send_to_addr(i, Format.event("LOBBY/READY", (conn.name, int(bool(player_readiness[0])))))

    if player_readiness[0]:
        start = True
        for ready in [i.ready for i in Connection.conns]:
            start = start and ready
        if start:
            self.game_starting = True
            return
    else:
        self.game_starting = False

@respond.event("COLOR_CHANGE")
def color_change(self: Server, addr: Address, message: tuple[int]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/COLOR_CHANGE", ["this game has already started."]))
    if addr not in [i.addr for i in Connection.conns]:
        self.send_to_addr(addr, Format.error("LOBBY/COLOR_CHANGE", ["you did not joined the lobby."]))
        return
    if message[0] in [conn.color for conn in Connection.conns]:
        self.send_to_addr(addr, Format.error("LOBBY/COLOR_CHANGE", ["this color is already taken."]))
        return
    if message[0] < 0:
        self.send_to_addr(addr, Format.error("LOBBY/COLOR_CHANGE", ["color is out of range. [0; +inf) are allowed."]))
        return
    conn = Connection.get_by_addr(addr)
    conn.color = message[0]
    for i in self.conns:
        self.send_to_addr(i, Format.event("LOBBY/COLOR_CHANGE", (conn.name, message[0])))

@respond.event("NATION_CHANGE")
def nation_change(self: Server, addr: Address, message: tuple[int]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/NATION_CHANGE", ["this game has already started."]))
        return
    if addr not in [i.addr for i in Connection.conns]:
        self.send_to_addr(addr, Format.error("LOBBY/NATION_CHANGE", ["you did not joined the lobby."]))
        return
    if not (0 <= message[0] < len(Nation.values())):
        self.send_to_addr(addr, Format.error("LOBBY/NATION_CHANGE", [f"nation is out of range. [0; {len(Nation.values())}) are allowed."]))
        return
    conn = Connection.get_by_addr(addr)
    conn.nation = message[0]
    for i in self.conns:
        self.send_to_addr(i, Format.event("LOBBY/NATION_CHANGE", (conn.name, message[0])))

@respond.event("ADMIN")
def eve_lobby_admin(self: Server, addr: Address, message: tuple[str]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/ADMIN", ["this game has already started."]))
        return
    if self.admin_addr == Address(("", 0)):
        self.send_to_addr(addr, Format.error("LOBBY/ADMIN", ["this lobby has admin."]))
        return
    if message[0] != self.password:
        self.send_to_addr(addr, Format.error("LOBBY/ADMIN", ["password is not correct."]))
        return
    self.admin_addr = addr

@respond.event("ADMIN/CHANGE_ORDER")
def eve_lobby_change_order(self: Server, addr: Address, message: tuple[str, str]):
    raise NotImplementedError("ADMIN/CHANGE_ORDER")

@respond.request("READINESS")
def req_readiness(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/READINESS", [(conn.name, conn.ready) for conn in Connection.conns]))

@respond.request("NAMES")
def req_readiness(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/NAMES", [conn.name for conn in Connection.conns]))

@respond.request("COLORS")
def req_color(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/COLORS", [(conn.name, conn.color) for conn in Connection.conns]))

@respond.request("NATIONS")
def req_color(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/NATIONS", [(conn.name, conn.color) for conn in Connection.conns]))