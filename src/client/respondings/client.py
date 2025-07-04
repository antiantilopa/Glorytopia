from serializator.client import Client as SerClient
from serializator.client import Respond
from shared import UnitData, CityData, TileData, TechNode
from enum import Enum
from typing import Callable
from copy import copy

class UpdateCodes(Enum):
    NOTHING = 0
    JOIN = 1
    DISCONNECT = 2
    READY = 3
    MESSAGE = 4
    COLOR_CHANGE = 5
    GAME_START = 6
    INIT_NAMES = 7
    INIT_COLORS = 8
    INIT_WORLD = 9
    UPDATE_UNIT = 10
    UPDATE_CITY = 11
    UPDATE_TILE = 12
    UPDATE_TECH = 13
    UPDATE_MONEY = 14
    END_TURN = 15
    RECONNECT = 16

respond = Respond()

@respond.event("DISCONNECT")
def disconnect(self: "Client", message: tuple[str]):
    if self.game_started:
        print(f"{message[0]} disconnected from the game.")
        return
    for name in self.readiness:
        self.readiness[name] = False
    for i in range(len(self.order)):
        if self.order[i] == message[0]:
            for j in range(i + 1, len(self.order)):
                self.order[j - 1] = self.order[j]
            self.order.pop(len(self.order) - 1)
            break
    self.readiness.pop(message[0])
    self.names.remove(message[0])
    self.updated |= 2 ** UpdateCodes.DISCONNECT.value

@respond.info("ORDER")
def print_order(self: "Client", message: list[str]):
    for i in range(len(message)):
        self.order[i] = message[i]

class Client(SerClient):
    object: "Client"

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

    def __init__(self):
        SerClient.__init__(self)
        self.respond.merge(respond)
        self.names: list[str] = []
        self.readiness: dict[str, bool] = {}
        self.names_to_colors: dict[str, int] = {} 
        self.game_started = False
        self.names: list[str] = []
        self.now_playing: int = 0
        self.order: dict[int, str] = {}
        self.messages: list[tuple[str, str]] = []
        self.myname: str = ""
        self.joined = None

        self.world_size = (0, 0)
        self.world: list[list[TileData]] = [[]]
        self.units: list[UnitData] = []
        self.cities: list[CityData] = []
        self.techs: list[TechNode] = []
        self.money = 0

        self.updated = 0
        self.world_updates: list[tuple[int, int]] = []
        self.units_updates: list[tuple[tuple[int, int], UnitData]] = []
        self.cities_updates: list[CityData] = []
        self.techs_updates: list[TechNode] = []
        self.object = self

        self.update_checkers: dict[int, Callable[[], None]] = {}
    
    def check_update(self, update_code: UpdateCodes):
        def decor(func: Callable[[], None]):
            def wrapper():
                if Client.object.updated & (2 ** update_code.value):
                    Client.object.updated &= ~(2 ** update_code.value)
                    func()
            self.update_checkers[update_code.value] = wrapper
            return wrapper
        return decor

    def check_updates(self):
        for code in copy(self.update_checkers):
            self.update_checkers[code]()
    
    def get_main_color(self, name: str) -> tuple[int, int, int]:
        if name in self.names_to_colors:
            return self.colors[self.names_to_colors[name]][0]
        return (255, 255, 255)
    
    def get_secondary_color(self, name: str) -> tuple[int, int, int]:
        if name in self.names_to_colors:
            return self.colors[self.names_to_colors[name]][1]
        return (0, 0, 0)