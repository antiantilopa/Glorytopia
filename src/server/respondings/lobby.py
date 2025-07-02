from serializator.host import Respond, Address
from serializator.data_format import Format
from .server import Server

respond = Respond("LOBBY")

@respond.event("JOIN")
def join(self: Server, addr: Address, name: tuple[str]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/JOIN", ["this game has already started."]))
        return
    if (name[0] in self.addrs_to_names.values()) or (name[0] == "") or not (name[0].isascii()):
        self.send_to_addr(addr, Format.error("LOBBY/JOIN", ["this name is already taken, or it is prohibited."]))
        return
    print(f"{name[0]} joined the game!")
    self.addrs_to_names[addr] = name[0]
    self.names_to_addrs[name[0]] = addr
    self.readiness[addr] = False
    self.game_starting = False
    self.order.append(addr)
    for j in self.conns:
        self.send_to_addr(j, Format.event("LOBBY/JOIN", [self.addrs_to_names[addr]]))

@respond.event("RECONNECT")
def reconnect(self: Server, addr: Address, name_and_recovery: tuple[str, int]):
    if not self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["this game has not started yet."]))
        return
    if addr in self.addrs_to_names:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["you are already connected."]))
        return
    name, recovery_code = name_and_recovery
    if name not in self.recovery_codes:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["you are not registered in this game."]))
        return
    if self.recovery_codes[name] != recovery_code:
        self.send_to_addr(addr, Format.error("LOBBY/RECONNECT", ["recovery code is not correct."]))
        return
    
    self.recovery_codes.pop(name)
    previous_addr = self.names_to_addrs[name]

    self.addrs_to_names[addr] = self.addrs_to_names.pop(previous_addr)
    self.players[addr] = self.players.pop(previous_addr)
    self.readiness[addr] = self.readiness.pop(previous_addr)
    self.order[self.order.index(previous_addr)] = addr
    self.names_to_addrs[name] = addr
    for j in self.conns:
        self.send_to_addr(j, Format.event("LOBBY/RECONNECT", [self.addrs_to_names[addr]]))

@respond.event("MESSAGE")
def message(self: Server, addr: Address, message: tuple[str]):
    if message[0] == "":
        self.send_to_addr(addr, Format.error("LOBBY/MESSAGE", ["message cannot be empty."]))
        return
    if len(message[0]) > 50:
        self.send_to_addr(addr, Format.error("LOBBY/MESSAGE", ["message is too long. 64 characters maximum."]))
        return
    print(f"<{self.addrs_to_names[addr]}> {message[0]}")
    for i in self.conns:
        self.send_to_addr(i, Format.event("LOBBY/MESSAGE", (self.addrs_to_names[addr], message[0])))

@respond.event("READY")
def ready(self: Server, addr: Address, player_readiness: tuple[int]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/READY", ["this game has already started."]))
        return
    if addr not in self.addrs_to_names:
        self.send_to_addr(addr, Format.error("LOBBY/READY", ["you did not joined the lobby."]))
        return
    print(f"! <{self.addrs_to_names[addr]}> ready = {(player_readiness[0])}")
    self.readiness[addr] = int(bool(player_readiness[0]))
    for i in self.conns:
        self.send_to_addr(i, Format.event("LOBBY/READY", (self.addrs_to_names[addr], int(bool(player_readiness[0])))))

    if player_readiness[0]:
        start = True
        for ready in self.readiness.values():
            start = start and ready
        if start:
            self.game_starting = True
            return
    else:
        self.game_starting = False

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
    addrind1 = self.order.index(self.names_to_addrs[message[0]])
    addrind2 = self.order.index(self.names_to_addrs[message[1]])
    self.order[addrind1], self.order[addrind2] = self.order[addrind2], self.order[addrind1] 
    self.send_to_addr(addr, Format.info("ORDER", self.order))

@respond.request("READINESS")
def req_readiness(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/READINESS", [(self.addrs_to_names[addr], self.readiness[addr]) for addr in self.readiness]))


@respond.request("NAMES")
def req_readiness(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/NAMES", [self.addrs_to_names[addr] for addr in self.addrs_to_names]))
