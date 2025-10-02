from netio import Host
from netio.datatypes import ConnectionData
from netio.router import ServerRouter
from netio.server import GameManager

from server.core.game import Game
from server.core.unit import Unit
from shared.player import PlayerData_

class GameServer(Host):
    game_started: bool
    game_starting: bool
    game_starting_timer: int
    max_players: int
    game_manager: "GameManager_"
    game: Game
    prohibited_names = ["never", "gonna", "give", "you", "up", "never", "gonna", "let", "down", "never", "gonna", "run", "around", "and", "desert", "you", "never", "gonna", "make", "you", "cry", "never", "gonna", "say", "goodbye", "never", "gonna", "tell", "you", "lies", "and", "hurt", "you"]

    obj: "GameServer" = None
    
    def __init__(self, host, port, max_players: int):
        super().__init__(host, port, ServerRouter(), PlayerData_, ConnectionData)
        self.game_started = False
        self.game = None
        self.max_players = max_players
        GameServer.obj = self
    
    def remove_dead_units(self):
        for unit in Unit.units:
            if unit.health <= 0:
                self.delete_object(unit)
        self.game.remove_dead_units()

class GameServerRouter(ServerRouter):
    host: GameServer

class GameManager_(GameManager):
    host: GameServer
    players: list[PlayerData_]