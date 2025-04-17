from typing import Any

REQUEST = "REQ"
INFO = "INF"
ERROR = "ERR"
EVENT = "EVE"

class Format:
    
    @staticmethod
    def error(route: str, message: tuple[Any]):
        return [ERROR, route, message]
    
    @staticmethod
    def info(route: str, message: tuple[Any]):
        return [INFO, route, message]
    
    @staticmethod
    def event(route: str, message: tuple[Any]):
        return [EVENT, route, message]
    
    @staticmethod
    def request(route: str, message: tuple[Any]):
        return [REQUEST, route, message]