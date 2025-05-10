from serializator.host import Respond, Address
from serializator.data_format import Format
from .server import Server

respond = Respond("LOBBY")

@respond.event("JOIN")
def join(self: Server, addr: Address, name: tuple[str]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/JOIN", ["this game has already started."]))
        self.conns[addr].close()
        return
    if name[0] in self.names_to_addrs or name[0] == "" or not name[0].isascii():
        self.send_to_addr(addr, Format.error("LOBBY/JOIN", ["this name is already taken, or it is prohoboted."]))
        return
    
    self.addrs_to_names[addr] = name[0]
    self.readiness[addr] = False
    self.order.append(addr)
    for j in self.conns:
        self.send_to_addr(j, Format.event("LOBBY/JOIN", [self.addrs_to_names[addr]]))

@respond.event("READY")
def ready(self: Server, addr: Address, player_readiness: tuple[int]):
    if self.game_started:
        self.send_to_addr(addr, Format.error("LOBBY/READY", ["this game has already started."]))
        return
    print(f"! <{self.addrs_to_names[addr]}> ready = {bool(player_readiness[0])}")
    self.readiness[addr] = int(bool(player_readiness[0]))
    for i in self.conns:
        if i == addr: continue
        self.send_to_addr(i, Format.info("READINESS", [(self.addrs_to_names[addr], int(bool(player_readiness[0])))]))

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
    self.send_to_addr(addr, Format.info("READINESS", [(self.addrs_to_names[addr], self.readiness[addr]) for addr in self.readiness]))


@respond.request("NAMES")
def req_readiness(self: Server, addr: Address, _: tuple):
    self.send_to_addr(addr, Format.info("LOBBY/NAMES", [self.addrs_to_names[addr] for addr in self.addrs_to_names]))
