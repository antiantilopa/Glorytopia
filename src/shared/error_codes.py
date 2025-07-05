from enum import Enum

class ErrorCodes(Enum):
    """
    This class contains error codes for various game-related errors.
    Each error code is represented as a class variable with a unique integer value.
    """

    # Error codes
    SUCCESS = 0
    ERR_NOT_IN_WORLD = 1
    ERR_TILE_HAS_NO_RESOURCE = 2
    ERR_NOT_ENOUGH_MONEY = 3
    ERR_NOT_IN_DOMAIN = 4
    ERR_THERE_IS_NO_SUITABLE_TECH = 5
    ERR_NOT_SUITABLE_TILE_TYPE = 6
    ERR_CITY_IS_FULL = 7
    ERR_NOT_YOUR_CITY = 8
    ERR_TECH_IS_ALREADY_RESEARCHED = 9
    ERR_UNIT_HAS_ALREADY_MOVED_OR_ATTACKED = 10
    ERR_NOT_YOUR_UNIT = 11
    ERR_NOT_EMPTY_TILE = 12
    ERR_NOT_SUITABLE_RESOURCE = 13
    ERR_NOT_SUITABLE_UNIT = 14
    ERR_NOT_SUITABLE_BUILDING = 15
    ERR_DEFAULT = 16
    ERR_NOT_A_CITY = 17
    ERR_BUILDING_HAS_NOT_ADJACENT_BONUS_GIVING_BUILDING = 18