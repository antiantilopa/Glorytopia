from serializator.host import Respond, Host, Address
from serializator.data_format import Format
from ..core import Player, Game
import socket

class Server(Host):
    def __init__(self):
        Host.__init__(self)
        self.conns: dict[Address, socket.socket] = {}
        self.names_to_addrs: dict[str, Address] = {}
        self.addrs_to_names: dict[Address, str] = {}
        self.readiness: dict[Address, bool] = {}
        self.order: list[Address] = []
        self.admin_addr: Address = Address(("", 0))
        self.game_started = False
        self.game_starting = False
        self.game_start_timer = 10
        self.password = None
        self.players: dict[Address, Player] = {}
        self.the_game: Game = None
        self.now_playing_player_index = 0