from engine_antiantilopa import Vector2d
from netio import Host
from netio.datatypes import ConnectionData
from netio.router import ServerRouter
from netio.serialization.serializer import Serializable
from netio.server import GameManager

from server.core.city import City
from server.core.game import Game
from server.core.tile import Tile
from server.core.unit import Unit
from server.core.game_event import GameEvent
from shared.player import PlayerData_


class GamePlayer(PlayerData_):
    joined_players: list["GamePlayer"] = []
    need_reconnect: list["GamePlayer"] = []

    @staticmethod
    def new_copy_from(pdata: "GamePlayer") -> "GamePlayer":
        new_obj = GamePlayer()
        new_obj.id = pdata.id
        new_obj.nickname = pdata.nickname
        new_obj.nation = pdata.nation
        new_obj.recovery_code = pdata.recovery_code
        new_obj.color = pdata.color
        return new_obj

    def copy_from(self, pdata: "GamePlayer") -> "GamePlayer":
        self.id = pdata.id
        self.nickname = pdata.nickname
        self.nation = pdata.nation
        self.recovery_code = pdata.recovery_code
        self.color = pdata.color

    def copy_to(self, pdata: "GamePlayer"):
        pdata.id = self.id
        pdata.nickname = self.nickname
        pdata.nation = self.nation
        pdata.recovery_code = self.recovery_code
        pdata.color = self.color


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
        super().__init__(host, port, ServerRouter(), GamePlayer, ConnectionData, GameManager_)
        self.game_started = False
        self.game = None
        self.max_players = max_players
        GameServer.obj = self
    
    def remove_dead_units(self):
        for unit in Unit.units:
            if unit.health <= 0:
                self.delete_object(unit)
        self.game.remove_dead_units()

    def create_new_objects(self):
        # HACK: better create new list for all new objects. also now only units are created dynamically, but maybe in future...
        for obj in Unit.units:
            if not self.game_manager.is_synchronized(obj):
                self.create_object(obj)

    # USE ONLY ONCE
    def create_all_objects(self):
        # HACK: also a bad decision, but whatever for now
        for city in City.cities:
            self.create_object(city)
        for unit in Unit.units:
            self.create_object(unit)
        for x in range(self.game.world.size.x):
            for y in range(self.game.world.size.y):
                tile = self.game.world.get(Vector2d(x, y))
                self.create_object(tile)

    def synchronize(self):
        GameEvent.record_changes()
        return super().synchronize()

class GameServerRouter(ServerRouter):
    host: GameServer

class GameManager_(GameManager):
    host: GameServer
    players: list[GamePlayer]

    def is_synchronized(self, obj: Serializable) -> bool:
        return obj in self._synchronized

    def synchronize(self):
        return GameManager.synchronize(self)