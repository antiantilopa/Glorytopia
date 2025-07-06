from serializator.client import Respond
from serializator.data_format import Format
from .client import Client, UpdateCodes

from shared import *

respond = Respond("GAME")

@respond.info("WORLD")
def get_world(self: Client, message: list[SerializedTile]):
    for sertile in message:
        tile = TileData.from_serializable(sertile)
        self.world[tile.pos.inty()][tile.pos.intx()] = tile
    for y in range(len(self.world)):
        for x in range(len(self.world[y])):
            if self.world[y][x] is not None:
                self.world_updates.append((x, y))
    self.updated |= 2 ** UpdateCodes.UPDATE_TILE.value
    
@respond.info("UNITS")
def get_units(self: Client, message: list[SerializedUnit]):
    for unit in self.units:
        self.units_updates.append((unit.pos.as_tuple(), ()))
    self.units = []
    
    for serunit in message:
        self.units.append(UnitData.from_serializable(serunit))
        self.units_updates.append(((), UnitData.from_serializable(serunit)))
    self.updated |= 2 ** UpdateCodes.UPDATE_UNIT.value

@respond.info("CITIES")
def get_cities(self: Client, message: list[SerializedCity]):
    self.cities = []
    for sercity in message:
        self.cities.append(CityData.from_serializable(sercity))
        self.cities_updates.append((CityData.from_serializable(sercity)))
    self.updated |= 2 ** UpdateCodes.UPDATE_CITY.value

@respond.info("NOW_PLAYING_PLAYER_INDEX")
def get_now_playing_player_index(self: Client, message: tuple[int]):
    self.now_playing = message[0]
    self.updated |= 2 ** UpdateCodes.END_TURN.value

@respond.info("MY_TECHS")
def get_techs(self: Client, message: tuple[int]):
    self.techs = [TechNode.by_id(i) for i in message]
    self.techs_updates = [TechNode.by_id(i) for i in message]
    self.updated |= 2 ** UpdateCodes.UPDATE_TECH.value

@respond.info("MY_MONEY")
def get_my_money(self: Client, message: list[int]):
    self.money = message[0]
    self.updated |= 2 ** UpdateCodes.UPDATE_MONEY.value

@respond.info("WORLD_SIZE")
def init_game(self: Client, message: tuple[int, int]):
    self.world_size = (message[0], message[1])
    self.world = [[None for x in range(message[0])] for y in range(message[1])]
    self.updated |= 2 ** UpdateCodes.INIT_WORLD.value