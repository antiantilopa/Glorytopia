from netio import Host
from netio.router import ServerRouter
from server.core.game import Game
from shared.connection_data import ConnectionData
from shared.player import PlayerData

class GameServer(Host):
    game_started: bool
    max_players: int
    game: Game
    
    def __init__(self, host, port, max_players: int):
        super().__init__(host, port, ServerRouter(), PlayerData, ConnectionData)
        self.game_started = False
        self.game = None
        self.max_players = max_players
