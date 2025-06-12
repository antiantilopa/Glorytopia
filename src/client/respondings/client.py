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
    GAME_START = 5
    INIT_NAMES = 6
    INIT_WORLD = 7
    UPDATE_UNIT = 8
    UPDATE_CITY = 9
    UPDATE_TILE = 10
    UPDATE_TECH = 11
    UPDATE_MONEY = 12
    END_TURN = 13

respond = Respond()
@respond.event("DISCONNECT")
def disconnect(self: "Client", message: tuple[str]):
    for name in self.readiness:
        self.readiness[name] = False
    print(message)
    print(self.names)
    self.readiness.pop(message[0])
    self.names.remove(message[0])
    self.updated |= 2 ** UpdateCodes.DISCONNECT.value

class Client(SerClient):
    object: "Client"

    def __init__(self):
        SerClient.__init__(self)
        self.respond.merge(respond)
        self.names: list[str] = []
        self.readiness: dict[str, bool] = {}
        self.game_started = False
        self.names: list[str] = []
        self.now_playing: int = 0
        self.order: dict[str, int] = {}
        self.messages: list[tuple[str, str]] = []
        self.myname: str = ""

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