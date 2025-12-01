import socket
import enum
import typing
import time
from ..logger import clientLogger
import threading
import types

_serializable_primitives = (int, str, float, bool, tuple, list, type(None))

T = typing.TypeVar("T")

class SerializationTypes(enum.Enum):
    STRING = 0
    INT32 = 1
    FLOAT32 = 2
    OBJECT = 3
    INT8 = 4
    NONE = 5
    NOTHING = 6
    LIST = 7
    
    UINT32 = 8
    UINT8 = 9

    END_OF_OBJECT = 255

class Tokens(enum.Enum):
    END_OF_STRING = b'\x00'

class SpecialTypes(enum.Enum):
    NOTHING = 0
    END = 1

class BaseWriter:
    writer_lock = threading.Lock()

    def encode(self, conn: socket.socket, message: tuple[int, str, tuple]):
        tp, route, data = message
        if isinstance(data, Serializable):
            data = data.serialize()
        elif not (isinstance(data, tuple) or isinstance(data, list)):
            data = (data, ) 
        serialized_message = bytearray()
        serialized_message.extend(self._int_to_bytes(tp, 2))
        serialized_message.extend(self._string_to_bytes(route))
        serialized_message.extend(self._object_to_bytes(data))
        with BaseWriter.writer_lock:
            conn.sendall(bytes(serialized_message))

    def _string_to_bytes(self, value: str) -> bytes:
        data = value.encode() + Tokens.END_OF_STRING.value
        return data
    
    def _boolean_to_bytes(self, value: bool) -> bytes:
        return bytes([int(value)])

    def _int_to_bytes(self, value: int, nbytes: int, signed: bool=True) -> bytes:
        return value.to_bytes(length=nbytes, signed=signed)

    def _float_to_bytes(self, value: float, nbytes: int) -> bytes:
        assert nbytes > 1, "Cannot serialize float in given amount of bytes"

        sign = value < 0
        mantissa, exponenta = (float(value).hex().split("p"))

        mantissa = mantissa.removeprefix("0x1.").removeprefix("-0x1.")

        exponenta = int(exponenta) + 127
        
        assert 256 > exponenta >= 0, "How the FUCK are you working with numbers so small/big ?!"

        mantissa[2 * nbytes + 1] = hex(int((float.fromhex(mantissa[2 * nbytes + 1]) // 2) * 2 + sign)).removeprefix("0x")

        ser_exp = self._int_to_bytes(exponenta, 1)
        data = bytearray()
        for i in range(nbytes):
            a = int(float.fromhex(mantissa[2 * i: 2 * i + 2]))
            data.extend(self._int_to_bytes(a, 1))

        return ser_exp + bytes(data)

    def _object_to_bytes(self, obj: tuple|list) -> bytes:
        data = bytearray()
        for field in obj:
            data.extend(self._any_to_bytes(field))
        end = bytes([SerializationTypes.END_OF_OBJECT.value])
        return bytes(data) + end

    def _any_to_bytes(self, obj: "int|float|str|bool|None|tuple|list|Serializable") -> bytes:
        start = bytes([0])
        data = bytes()
        if isinstance(obj, bool):
            start = bytes([SerializationTypes.INT8.value])
            data = self._boolean_to_bytes(obj)
        elif isinstance(obj, str):
            start = (bytes([SerializationTypes.STRING.value]))
            data = self._string_to_bytes(obj)
        elif isinstance(obj, float):
            start = (bytes([SerializationTypes.FLOAT32.value]))
            data =self._float_to_bytes(obj, 4)
        elif isinstance(obj, int):
            if -128 <= obj < 128:
                start = (bytes([SerializationTypes.INT8.value]))
                data = self._int_to_bytes(obj, 1)
            elif 0 <= obj < 256:
                start = (bytes([SerializationTypes.UINT8.value]))
                data = self._int_to_bytes(obj, 1, signed=0)
            elif 0 <= obj:
                start = (bytes([SerializationTypes.UINT32.value]))
                data = self._int_to_bytes(obj, 4, signed=0)
            else:
                start = (bytes([SerializationTypes.INT32.value]))
                data = self._int_to_bytes(obj, 4)
        elif isinstance(obj, tuple):
            start = (bytes([SerializationTypes.OBJECT.value]))
            data = self._object_to_bytes(obj)
        elif isinstance(obj, list):
            start = (bytes([SerializationTypes.LIST.value]))
            data = self._object_to_bytes(obj)
        elif isinstance(obj, Serializable):
            start = (bytes([SerializationTypes.OBJECT.value]))
            data = self._object_to_bytes(obj.serialize())
        elif obj == None:
            start = (bytes([SerializationTypes.NONE.value]))
        elif obj == SpecialTypes.NOTHING:
            start = (bytes([SerializationTypes.NOTHING.value]))
        else:
            raise ValueError(f"Unsupported serialization type: {obj}")
        return start + data
    
class BaseReader:

    def decode(self, conn: socket.socket) -> tuple[int, str, tuple]:
        tp = self._read_int(conn, 2)
        route = self._read_string(conn)
        data = self._read_object(conn)
        return tp, route, data
    
    def _read_field(self, conn: socket.socket):
        tp = recv_from(conn, 1)
        
        match(tp[0]):
            case SerializationTypes.STRING.value:
                return self._read_string(conn)
            case SerializationTypes.INT8.value:
                return self._read_int(conn, 1)
            case SerializationTypes.UINT8.value:
                return self._read_int(conn, 1, 0)
            case SerializationTypes.INT32.value:
                return self._read_int(conn, 4)
            case SerializationTypes.UINT32.value:
                return self._read_int(conn, 4, 0)
            case SerializationTypes.FLOAT32.value:
                return self._read_float(conn, 4)
            case SerializationTypes.OBJECT.value:
                return self._read_object(conn)
            case SerializationTypes.LIST.value:
                return list(self._read_object(conn))
            case SerializationTypes.NONE.value:
                return None
            case SerializationTypes.NOTHING.value:
                return SpecialTypes.NOTHING
            case SerializationTypes.END_OF_OBJECT.value:
                return SpecialTypes.END
        
        raise ValueError(f"Unknown serialized type: {tp[0]}")  
    
    def _read_string(self, conn: socket.socket) -> str:
        data = bytes()
        while (bt := recv_from(conn, 1)) != Tokens.END_OF_STRING.value:
            data += bt
        return data.decode()
    
    def _read_boolean(self, conn: socket.socket) -> bool:
        val = recv_from(conn, 1)
        return int(val[0])
    
    def _read_int(self, conn: socket.socket, nbytes: int, signed: bool=True) -> int:
        return int.from_bytes(recv_from(conn, nbytes), signed=signed)
    
    def _read_float(self, conn: socket.socket, nbytes: int) -> float:
        assert nbytes % 2 == 0, "Cannot deserialize odd amount of bytes"
        exp = int.from_bytes(recv_from(conn, 1)) - 127
        mantissa = int.from_bytes(recv_from(conn, nbytes - 1))

        sign = mantissa % 2
        if sign == 0:
            mantissa += 1

        return mantissa * (2 ** exp) * (-1 if sign else 1)

    def _read_object(self, conn: socket.socket) -> tuple:
        obj = []
        while (field := self._read_field(conn)) != SpecialTypes.END:
            obj.append(field)
        return tuple(obj)

    def _bytes_to_serialized(self, data: bytes|bytearray, start: int = 0) -> tuple[str|int|float|tuple|bool|None|SpecialTypes|list, int]:
        typ = data[start]
        start += 1
        match typ:
            case SerializationTypes.STRING.value:
                result = ""
                while data[start] != 0:
                    result += chr(data[start])
                    start += 1
                return result, len(result) + 1
            case SerializationTypes.INT32.value:
                result = int.from_bytes(data[start : start + 4], signed=1)
                return result, 4
            case SerializationTypes.UINT32.value:
                result = int.from_bytes(data[start : start + 4], signed=0)
                return result, 4
            case SerializationTypes.INT8.value:
                result = int.from_bytes(data[start : start + 1], signed=1)
                return result, 1
            case SerializationTypes.UINT8.value:
                result = int.from_bytes(data[start : start + 1], signed=0)
                return result, 1
            case SerializationTypes.FLOAT32.value:
                result = ...
                return NotImplemented, 4
            case SerializationTypes.OBJECT.value:
                result = []
                tmp = start
                while data[start] != SerializationTypes.END_OF_OBJECT.value:
                    field, length = self._bytes_to_serialized(data, start)
                    result.append(field)
                    start += length + 1
                return tuple(result), start - tmp + 1
            case SerializationTypes.INT8.value:
                result = int(data[start])
                return result, 1
            case SerializationTypes.NONE.value:
                return None, 0
            case SerializationTypes.NOTHING.value:
                return SpecialTypes.NOTHING, 0
            case SerializationTypes.LIST.value:
                result = []
                tmp = start
                while data[start] != SerializationTypes.END_OF_OBJECT.value:
                    field, length = self._bytes_to_serialized(data, start)
                    result.append(field)
                    start += length + 1
                return result, start - tmp + 1

class SerializeField:
    def __init__(self, by_id=False):
        self.by_id = by_id

class ObservableList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updated = False

    def mark(self):
        self.updated = False

    def __setitem__(self, i, v):
        self.updated = True
        return super().__setitem__(i, v)

    def append(self, v):
        self.updated = True
        return super().append(v)

    def extend(self, it):
        self.updated = True
        return super().extend(it)

    def insert(self, i, v):
        self.updated = True
        return super().insert(i, v)

    def remove(self, v):
        self.updated = True
        return super().remove(v)

    def pop(self, i=-1):
        self.updated = True
        return super().pop(i)

    def clear(self):
        self.updated = True
        return super().clear()

    def sort(self, *a, **kw):
        self.updated = True
        return super().sort(*a, **kw)

    def reverse(self):
        self.updated = True
        return super().reverse()
    
class Serializable:
    __updates: dict
    _class_id: typing.Annotated[int, SerializeField()]
    _id: typing.Annotated[int, SerializeField()]
    is_created: bool

    __classes: list[type["Serializable"]] = []
    _primitive: bool = False
    _serialize_by_id: bool = False
    __ID: int = 0

    def __init_subclass__(cls, primitive: bool = None, by_id: bool = None):
        if cls.__qualname__ in [c.__qualname__ for c in Serializable.__classes]:
            raise ValueError(f"two classes with the same name: {cls.__qualname__}")
        cls._primitive = cls._primitive if primitive is None else primitive
        cls._serialize_by_id = cls._serialize_by_id if by_id is None else by_id
        Serializable.__classes.append(cls)
        orig_init = cls.__init__

        cls._class_id = get_class_id(cls)

        def new_init(self: Serializable, *a, **kw):
            self.__updates = {}

            orig_init(self, *a, **kw)
            self.is_created = False
            self._id = Serializable.__ID
            Serializable.__ID += 1

            for key, value in get_all_annotations(self).items():
                attr = getattr(self, key, None)
                if attr != None and isinstance(attr, list):
                    setattr(self, key, ObservableList(attr))

            self._clear_updates()

        if not cls._primitive:
            cls.__init__ = new_init

    @staticmethod
    def get_class(tid: int) -> type["Serializable"]:
        for cls in Serializable.__classes:
            if get_class_id(cls) == tid:
                return cls
        raise ValueError("No class with id: ", tid)

    @staticmethod 
    def parse(data, cls: type[T], ignore_class_id: bool = False, init_for_serializables: bool = False) -> T:
        if cls is None:
            return data
        
        if data == SpecialTypes.NOTHING:
            return SpecialTypes.NOTHING
        
        generic = None
        if typing.get_origin(cls) is not None:
            generic = cls
            cls = typing.get_origin(cls)

        if isinstance(data, type(None)):
            return None
        
        if isinstance(data, (int, float, bool, str)):
            if issubclass(cls, Serializable) and cls._primitive:
                return cls(*data)
            if _check_classes(type(data), cls):
                raise ValueError(f"Classes don't match: {type(data)} {cls}")
            return data
        
        if issubclass(cls, tuple) and isinstance(data, tuple) and generic is None:
            return data

        if issubclass(cls, Serializable) and cls._serialize_by_id:
            if not isinstance(data, tuple) or len(data) != 2:
                raise ValueError(f"Invalid ID serialization. got {data} for {generic if generic is not None else cls}")
            if not ignore_class_id:
                if get_class_id(cls) != data[0]:
                    clientLogger.warning(f"Class ids doesn't match: expected {cls}, got {Serializable.get_class(data[0])}")
                    cls = Serializable.get_class(data[0])

            return cls.by_id(data[1])
        if issubclass(cls, Serializable):
            if cls._primitive:
                return cls(*data)
            else:
                return cls.deserialize(data, ignore_class_id, init_for_serializables)

        if issubclass(cls, list) and generic is not None:
            tp = typing.get_args(generic)[0]

            return ObservableList([Serializable.parse(i, tp, ignore_class_id, init_for_serializables) for i in data])

        if issubclass(cls, list) and generic is None:

            return ObservableList(data)

        if issubclass(cls, tuple) and generic is not None:
            tps = typing.get_args(generic)

            assert len(data) == len(tps), f"Invalid data {data} length for {generic}"

            return tuple(Serializable.parse(data[i], tps[i], ignore_class_id, init_for_serializables) for i in range(len(tps)))

        raise ValueError(f"Wrong type was passed: got {type(data)} of {data}, expected {cls if generic is None else generic}")
        
    @classmethod
    def deserialize(cls, data: tuple, ignore_class_id: bool = False, init_for_serializables: bool = False) -> typing.Self:
        if cls._primitive:
            return cls(*data) 

        if not ignore_class_id:
            if get_class_id(cls) != data[0]:
                clientLogger.warning(f"Class ids doesn't match: expected {cls}, got {Serializable.get_class(data[0])}")
                cls = Serializable.get_class(data[0])
            
        obj = cls.__new__(cls)
        ant = get_all_annotations(cls)
        for i, (key, value) in enumerate(ant.items()):
            metadata = value.__metadata__[0]
            assert isinstance(metadata, SerializeField)

            field_cls = value.__origin__

            if type(field_cls) is types.UnionType:
                field_cls = field_cls.__args__[0]

            if data[i] != SpecialTypes.NOTHING:
                super().__setattr__(obj, key, Serializable.parse(data[i], field_cls, ignore_class_id))

        if init_for_serializables:
            obj.__updates = {}

            obj.is_created = False
            obj._id = Serializable.__ID
            Serializable.__ID += 1

            for key, value in get_all_annotations(obj).items():
                attr = getattr(obj, key, None)
                if attr != None and isinstance(attr, list):
                    setattr(obj, key, ObservableList(attr))

        return obj

    def init(self):
        self.__updates = {}

        self.is_created = False
        self._id = Serializable.__ID
        Serializable.__ID += 1

        for key, value in get_all_annotations(self).items():
            attr = getattr(self, key, None)
            if attr != None and isinstance(attr, list):
                setattr(self, key, ObservableList(attr))

        self._clear_updates()

    def serialize(self) -> tuple:
        if self._primitive:
            return self.__tuple__()
        if self._serialize_by_id:
            return (get_class_id(type(self)), self.id)
        data = []
        for key, cls in get_all_annotations(self).items():
            if _is_annotated(cls):
                metadata = cls.__metadata__[0]
                assert isinstance(metadata, SerializeField)

                value = getattr(self, key)

                if isinstance(value, ObservableList):
                    data.append(to_prim(value))
                    continue

                if isinstance(value, _serializable_primitives):
                    data.append(value)
                    continue

                assert isinstance(value, Serializable), "Field type should be subclass of Serializable to serialize"
                
                data.append(value.serialize())
        return tuple(data)
    
    def __setattr__(self, name, value):
        cls = get_all_annotations(self).get(name)
        if cls != None:
            self.__updates[name] = value

        super().__setattr__(name, value)

    def _clear_updates(self):
        self.__updates.clear()
        for key, cls in get_all_annotations(self).items():
            new_value = getattr(self, key, None)

            if isinstance(new_value, ObservableList):
                new_value.mark()
                continue

            if isinstance(new_value, Serializable) and not new_value._primitive:
                new_value._clear_updates()
                continue
            
    def _get_updates(self):
        return self.__updates
    
    def serialize_updates(self) -> tuple | SpecialTypes:
        data = []
        for key, cls in get_all_annotations(self).items():
            metadata = cls.__metadata__[0]
            assert isinstance(metadata, SerializeField)

            value = self.__updates.get(key, SpecialTypes.NOTHING)
            new_value = getattr(self, key)

            if key in ('_id', '_class_id'):
                data.append(new_value)
                continue

            if value == SpecialTypes.NOTHING and isinstance(new_value, ObservableList):
                if new_value.updated:
                    data.append(to_prim(new_value))
                else:
                    data.append(SpecialTypes.NOTHING)
                continue

            # Add changes of field
            if value == SpecialTypes.NOTHING and isinstance(new_value, Serializable) and not new_value._primitive and not new_value._serialize_by_id:
                data.append(_optimize_nothings(new_value.serialize_updates()))
                continue

            # Check if primitive type
            if isinstance(value, _serializable_primitives) or value == SpecialTypes.NOTHING:
                data.append(value)
                continue

            assert isinstance(value, Serializable), f"Field type should be subclass of Serializable to serialize, not {type(value)} of {value}"

            if new_value._serialize_by_id:
                data.append((get_class_id(type(value)), value.id))
                continue

            data.append(value.serialize())

        return _optimize_nothings(tuple(data))
    
    def deserialize_updates(self, data: tuple) -> typing.Self:
        obj = self
        for i, (key, value) in enumerate(get_all_annotations(obj).items()):
            metadata = value.__metadata__[0]
            assert isinstance(metadata, SerializeField)

            field_cls = value.__origin__

            if data[i] == SpecialTypes.NOTHING:
                continue

            if type(field_cls) is types.UnionType:
                field_cls = field_cls.__args__[0]

            if typing.get_origin(field_cls):
                field_cls = typing.get_origin(field_cls)
                
            if issubclass(field_cls, Serializable) and not field_cls._serialize_by_id and not field_cls._primitive:
                field_cls.deserialize_updates(getattr(obj, key), data[i])
                continue
            
            object.__setattr__(obj, key, Serializable.parse(data[i], field_cls))
        return obj

    def validate(self, player_data) -> bool:
        return bool(self.serialize())
    
    def client_on_create(self):
        pass
    
    def client_on_update(self):
        pass

    def client_on_destroy(self):
        pass

def _check_classes(cls1, cls2):
    return not (issubclass(cls1, cls2) or issubclass(cls2, cls1) or issubclass(cls1, type(None)) or issubclass(cls2, type(None)))

def to_prim(obj: tuple | int | bool | float | list | Serializable | type[None] | str):
    if isinstance(obj, (int, bool, float, str, type(None))):
        return obj
    
    if isinstance(obj, (tuple, list)):
        nw = []
        for i in obj:
            nw.append(to_prim(i))
        return nw

    if isinstance(obj, Serializable):
        return obj.serialize()

    raise ValueError("Object is not serializable,", obj)

def get_all_annotations(obj_or_cls) -> dict[str, type]:
    cls = obj_or_cls if isinstance(obj_or_cls, type) else type(obj_or_cls)
    
    annotations = {}
    for base in reversed(cls.__mro__):
        if base is object:
            continue
        for key, value in base.__annotations__.items():
            if _is_annotated(value):
                annotations[key] = value
    return annotations

def _optimize_nothings(data: tuple):
    flag = any(i != SpecialTypes.NOTHING for i in data[2:])  # Skip _id
    return data if flag else SpecialTypes.NOTHING

def _is_annotated(cls) -> bool:
    return typing.get_origin(cls) is typing.Annotated and len(cls.__metadata__) > 0 and isinstance(cls.__metadata__[0], SerializeField)

def get_class_id(cls):
    name = cls.__qualname__
    return _hash(name, int(1e9 + 7))
    
def _hash(s: str, mod: int) -> int:
    hash_sum = 0
    for i, c in enumerate(s):
        hash_sum += pow(ord(c), i, mod)
    return hash_sum % mod

def recv_from(conn: socket.socket, bufsize: int, flags: int = 0):
    assert bufsize > 0
    result = conn.recv(bufsize, flags)
    if len(result) == 0:
        raise ConnectionResetError(conn)
    return result