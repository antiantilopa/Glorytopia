from netio import *
from shared import UnitData, CityData, TileData, TechNode, PlayerData_
from enum import Enum
from typing import Callable
from copy import copy

from shared.util.position import Pos

respond = ClientRouter()

class GamePlayer(PlayerData_):
    money: int
    techs: list[TechNode]
    vision: list[list[bool]]

    joined_players: list["GamePlayer"] = []
    disconnected: list["GamePlayer"] = []
    colors = [ # Should be in resource pack or smth TODO
        ((255, 0, 0), (255, 255, 255)),   # Red - White
        ((0, 255, 0), (0, 0, 0)),   # Green
        ((0, 0, 255), (255, 255, 255)),   # Blue - White
        ((255, 255, 0), (0, 0, 0)),   # Yellow - Black
        ((255, 165, 0), (0, 0, 0)),   # Orange - Black
        ((128, 0, 128), (255, 255, 255)),   # Purple - White
        ((192, 192, 192), (0, 0, 0)),   # Silver - Black
        ((0, 128, 128), (255, 255, 255)),   # Teal - White
    ]
    def get_main_color(self):
        return GamePlayer.colors[self.color][0]

    def get_secondary_color(self):
        return GamePlayer.colors[self.color][1]

    @staticmethod
    def by_id(id: int):
        for p in GamePlayer.joined_players:
            if p.id == id:
                return p

    def set_vision(self, line_vision: list[bool], world_size: Pos):
        # line_vision will have some unnesecarry zeros at the end
        assert len(line_vision) >= world_size.x * world_size.y
        self.vision = [[line_vision[i + j * world_size.x] for i in range(world_size.x)] for j in range(world_size.y)]

    def client_on_create(self):
        if GameClient.object.game_started:
            return
        if self.joined and (self not in GamePlayer.joined_players):
            GamePlayer.joined_players.append(self)

    def client_on_update(self):
        if GameClient.object.game_started:
            if not self.joined:
                GamePlayer.disconnected.append(self)
                return
            disconnected_me = [self.nickname == p.nickname for p in GamePlayer.disconnected]
            if len(disconnected_me) == 1:
                disconnected_me = disconnected_me[0]
                GamePlayer.disconnected.remove(disconnected_me)
                GamePlayer.joined_players.remove(disconnected_me)
                GamePlayer.joined_players.append(self)
            return
        
        if self.joined and (self not in GamePlayer.joined_players):
            GamePlayer.joined_players.append(self)
        elif (not self.joined) and (self in GamePlayer.joined_players):
            GamePlayer.joined_players.remove(self)
    
    def client_on_destroy(self):
        if GameClient.object.game_started:
            if self.joined:
                GamePlayer.disconnected.append(self)
            return
        if self.joined and (self in GamePlayer.joined_players):
            GamePlayer.joined_players.remove(self)

    def __str__(self):
        return f"PlayerData <{self.nickname}>"

    def __repr__(self):
        return f"PlayerData <{self.nickname}>"
    

class GameClientRouter(ClientRouter):
    routers: list["GameClientRouter"] = []

    def __init__(self, default=""):
        ClientRouter.__init__(self, default)
        GameClientRouter.routers.append(self)

class GameClient(Client):
    object: "GameClient" = None

    now_playing_player_id: int
    game_started: bool
    me: GamePlayer

    def __init__(self, host: str, port: int):
        Client.__init__(self, host, port, GameClientRouter(), GamePlayer)
        self.now_playing_player_id = 0
        self.game_started = 0
        for router in GameClientRouter.routers:
            self.router.merge(router)
        GameClient.object = self
        self.start()