import socket
import logging
from typing import Callable, Any, get_origin

from .serialization.serializer import Serializable, SerializeField
from .datatypes import PlayerData, Address, ConnectionData
from .logger import serverLogger, clientLogger

from . import client as Client
from . import server as Server

class BaseRouter:

    default: str

    _merged_routers: list["BaseRouter"]
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
        self._merged_routers = []
        
    def on_connect(self):
        def wrapper(func):
            self._on_connect = func
        return wrapper
    
    def on_disconnect(self):
        def wrapper(func):
            self._on_disconnect = func
        return wrapper

    def event(self, route="", datatype=None):
        check_datatype(datatype)

        if self.default != "":
            route = self.default + "/" + route
        
        def wrapper(func):
            self._event_handlers[route] = (func, datatype)

        return wrapper

    def response(self, route="", datatype=None):
        check_datatype(datatype)

        if self.default != "":
            route = self.default + "/" + route
        
        def wrapper(func):
            self._response_handlers[route] = (func, datatype)

        return wrapper

    def request(self, route="", datatype=None):
        check_datatype(datatype)
        
        if self.default != "":
            route = self.default + "/" + route

        def wrapper(func):
            self._request_handlers[route] = (func, datatype)

        return wrapper
    
    def fire_event(self, route: str, data: tuple):
        if route not in self._event_handlers.keys():
            logging.warning("Route %s not found.", route)
            return

        handler, cls = self._event_handlers[route]
        
        handler(parse_data(data, cls))

    def handle_request(self, route: str, data: tuple) -> tuple | Serializable:
        handler, cls = self._request_handlers[route]
        
        return handler(parse_data(data, cls))

    def handle_response(self, route: str, data: tuple):
        handler, cls = self._response_handlers[route]
        
        handler(parse_data(data, cls))

    def merge(self, other: "BaseRouter"):
        self._response_handlers.update(other._response_handlers)
        self._request_handlers.update(other._request_handlers)
        self._event_handlers.update(other._event_handlers)
        if other._on_disconnect is not None:
            self._on_disconnect = other._on_disconnect
        if other._on_connect is not None:
            self._on_connect = other._on_connect

class ClientRouter(BaseRouter):
    client: "Client.Client"
    
    _merged_routers: list["ClientRouter"]
    
    def handle_request(self, route, data):
        raise NotImplementedError("Are you sure this should be called?")

    def merge(self, other: "ClientRouter"):
        if other == self:
            return
        BaseRouter.merge(self, other)
        if isinstance(other, ClientRouter): 
            self._merged_routers.append(other)
            other.set_client(self.client)

    def set_client(self, client: "Client.Client"):
        self.client = client
        for router in self._merged_routers:
            router.set_client(client)

class ServerRouter(BaseRouter):
    
    host: "Server.Host"
    
    _response_handlers: dict[str, tuple[Callable[[PlayerData, tuple], None], type[Serializable] | None]]
    _request_handlers: dict[str, tuple[Callable[[PlayerData, tuple], tuple | Serializable], type[Serializable] | None]]
    _event_handlers: dict[str, tuple[Callable[[PlayerData, tuple], None], type[Serializable] | None]]

    _merged_routers: list["ServerRouter"]

    def merge(self, other: "ServerRouter"):
        BaseRouter.merge(self, other)
        if isinstance(other, ServerRouter): 
            self._merged_routers.append(other)
            other.set_host(self.host)

    def set_host(self, host: "Server.Host"):
        self.host = host
        for router in self._merged_routers:
            router.set_host(host)

    def fire_event(self, route: str, player_data: Serializable, data: tuple):
        if route not in self._event_handlers.keys():
            serverLogger.warning("Route %s not found.", route)
            return
        
        handler, cls = self._event_handlers[route]

        handler(player_data, parse_data(data, cls))

    def handle_request(self, route: str, player_data: Serializable, data: tuple) -> tuple | Serializable:
        handler, cls = self._request_handlers[route]
        
        return handler(player_data, parse_data(data, cls))

    def handle_response(self, route: str, player_data: Serializable, data: tuple):
        handler, cls = self._response_handlers[route]
        
        handler(player_data, parse_data(data, cls))

    def handle_response(self, route, data):
        raise NotImplementedError("Are you sure this should be called?")
    
def check_datatype(datatype: type = None) -> bool:
    return 1 

def parse_data(data: tuple|Serializable, cls: type):
    origin = get_origin(cls)
    if origin is None: origin = cls
    if cls is None:
        assert (len(data) == 0) or (len(data) == 1 and data[0] is None), f"datatype is {cls}, got {data}"
        return None
    if issubclass(origin, tuple) or issubclass(origin, list) or issubclass(origin, Serializable):
        return Serializable.parse(data, cls)
    else:
        result = Serializable.parse(data[0], cls)
        # assert len(result) == 1, f"datatype is {cls}, got {data}"
        return result