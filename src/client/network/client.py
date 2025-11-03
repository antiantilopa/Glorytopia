from netio import *
from shared import UnitData, CityData, TileData, TechNode, PlayerData_
from enum import Enum
from typing import Callable
from copy import copy

respond = ClientRouter()

class GamePlayer(PlayerData_):
    pass

class GameClientRouter(ClientRouter):
    pass

class GameClient(Client):
    object: "GameClient" = None

    colors = [
        ((255, 0, 0), (255, 255, 255)),   # Red - White
        ((0, 255, 0), (0, 0, 0)),   # Green
        ((0, 0, 255), (255, 255, 255)),   # Blue - White
        ((255, 255, 0), (0, 0, 0)),   # Yellow - Black
        ((255, 165, 0), (0, 0, 0)),   # Orange - Black
        ((128, 0, 128), (255, 255, 255)),   # Purple - White
        ((192, 192, 192), (0, 0, 0)),   # Silver - Black
        ((0, 128, 128), (255, 255, 255)),   # Teal - White
    ]

    def __init__(self, host: str, port: int):
        Client.__init__(self, host, port, GameClientRouter(), GamePlayer)
        self.object = self

    def get_main_color(self, name: str) -> tuple[int, int, int]: ...

    def get_secondary_color(self, name: str) -> tuple[int, int, int]: ...