import socket
import logging
from typing import Callable, Any

from .serialization.serializer import Serializable
from .datatypes import PlayerData, Address, ConnectionData
from .logger import serverLogger, clientLogger

class BaseRouter:

    default: str

    _on_connect: Callable[[ConnectionData], bool] | None
    _on_disconnect: Callable[[PlayerData], None] | None

    _response_handlers: dict[str, tuple[Callable[[tuple], None], type[Serializable] | None]]
    _request_handlers: dict[str, tuple[Callable[[tuple], tuple | Serializable], type[Serializable] | None]]
    _event_handlers: dict[str, tuple[Callable[[tuple], None], type[Serializable] | None]]

    def __init__(self, default = ""):
        self.default = default
        self._on_connect = None
        self._on_disconnect = None
        self._response_handlers = {}
        self._request_handlers = {}
        self._event_handlers = {}
        
    def on_connect(self):
        def wrapper(func):
            self._on_connect = func
        return wrapper
    
    def on_disconnect(self):
        def wrapper(func):
            self._on_disconnect = func
        return wrapper

    def event(self, route="", datatype=None):
        if datatype and not issubclass(datatype, Serializable):
            raise TypeError("Datatype should be subclass of Serializable.")
        
        def wrapper(func):
            self._event_handlers[route] = (func, datatype)

        return wrapper

    def response(self, route="", datatype=None):
        if datatype and not issubclass(datatype, Serializable):
            raise TypeError("Datatype should be subclass of Serializable.")
        
        def wrapper(func):
            self._response_handlers[route] = (func, datatype)

        return wrapper

    def request(self, route="", datatype=None):
        if datatype and not issubclass(datatype, Serializable):
            raise TypeError("Datatype should be subclass of Serializable.")
        
        def wrapper(func):
            self._request_handlers[route] = (func, datatype)

        return wrapper
    
    def fire_event(self, route: str, data: tuple):
        if route not in self._event_handlers.keys():
            logging.warning("Route %s not found.", route)
            return

        handler, cls = self._event_handlers[route]
        if not cls:
            handler(data)
        else:
            handler(cls.deserialize(data))

    def handle_request(self, route: str, data: tuple) -> tuple | Serializable:
        handler, cls = self._request_handlers[route]
        if not cls:
            return handler(data)
        else:
            return handler(cls.deserialize(data))

    def handle_response(self, route: str, data: tuple):
        handler, cls = self._response_handlers[route]
        if not cls:
            handler(data)
        else:
            handler(cls.deserialize(data))

    def merge(self, other: "BaseRouter"):
        self._response_handlers.update(other._response_handlers)
        self._request_handlers.update(other._request_handlers)
        self._event_handlers.update(other._event_handlers)


class ClientRouter(BaseRouter):
    from . import client as Client

    client: "Client.Client"
    
    def handle_request(self, route, data):
        raise NotImplementedError("Are you sure this should be called?")


class ServerRouter(BaseRouter):
    from . import server as Server
    
    host: "Server.Host"
    
    _response_handlers: dict[str, tuple[Callable[[PlayerData, tuple], None], type[Serializable] | None]]
    _request_handlers: dict[str, tuple[Callable[[PlayerData, tuple], tuple | Serializable], type[Serializable] | None]]
    _event_handlers: dict[str, tuple[Callable[[PlayerData, tuple], None], type[Serializable] | None]]

    def fire_event(self, route: str, player_data: Serializable, data: tuple):
        if route not in self._event_handlers.keys():
            serverLogger.warning("Route %s not found.", route)
            return
        
        handler, cls = self._event_handlers[route]
        if not cls:
            handler(player_data, data)
        else:
            handler(player_data, cls.deserialize(data))

    def handle_request(self, route: str, player_data: Serializable, data: tuple) -> tuple | Serializable:
        handler, cls = self._request_handlers[route]
        if not cls:
            return handler(player_data, data)
        else:
            return handler(player_data, cls.deserialize(data))

    def handle_response(self, route: str, player_data: Serializable, data: tuple):
        handler, cls = self._response_handlers[route]
        if not cls:
            handler(player_data, data)
        else:
            handler(player_data, cls.deserialize(data))

    def handle_response(self, route, data):
        raise NotImplementedError("Are you sure this should be called?")
    
