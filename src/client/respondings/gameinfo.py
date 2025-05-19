from serializator.client import Respond
from serializator.data_format import Format
from .client import Client

from shared import *

respond = Respond("GAME")

@respond.info("GAME/WORLD")
def get_world(self: Client, message: list[SerializedTile]):
    for sertile in message:
        tile = TileData.from_serializable(sertile)
        self.world[tile.pos.inty()][tile.pos.intx()] = tile

@respond.info("GAME/UNITS")
def get_units(self: Client, message: list[SerializedUnit]):
    units = []
    for serunit in message:
        units.append(UnitData.from_serializable(serunit))

@respond.info("GAME/CITIES")
def get_cities(self: Client, message: list[SerializedCity]):
    self.cities = []
    for sercity in message:
        self.cities.append(CityData.from_serializable(sercity))

@respond.info("GAME/MY_TECHS")
def get_techs(self: Client, message: tuple[int]):
    self.techs = [TechNode.by_id(i) for i in message]

@respond.info("GAME/MY_MONEY")
def get_my_money(self: Client, message: list[int]):
    self.money = message[0]