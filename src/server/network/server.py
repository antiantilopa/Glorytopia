from serializator.host import Respond, Host, Address
from serializator.data_format import Format
from ..core import Player, Game
import socket

class Connection:
    conn: socket.socket
    addr: Address
    name: str
    ready: bool
    recovery_code: int
    color: int
    nation: int
    idx: int
    player: Player

    IDX = 0
    conns: list["Connection"] = []

    def __init__(self, addr: Address, name: str, conn: socket.socket):
        self.idx = Connection.IDX
        Connection.IDX += 1
        self.addr = addr
        self.conn = conn
        self.name = name
        self.color = 0
        self.nation = 0
        self.ready = 0
        Connection.conns.append(self)
    
    @staticmethod
    def get_by_name(name: str) -> "Connection":
        for conn in Connection.conns:
            if conn.name == name:
                return conn
        raise KeyError(f"No connection with name: {name}")
    
    @staticmethod
    def get_by_addr(addr: Address) -> "Connection":
        for conn in Connection.conns:
            if conn.addr == addr:
                return conn
        raise KeyError(f"No connection with address: {addr}")


class Server(Host):

    def __init__(self):
        Host.__init__(self)
        self.admin_addr: Address = Address(("", 0))
        self.game_started = False
        self.game_starting = False
        self.game_start_timer = 10
        self.password = None
        self.the_game: Game = None
