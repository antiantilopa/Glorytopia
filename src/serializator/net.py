import socket, threading
from typing import Any

class SerializationTypes:
    END = 0
    CHAR = 1
    SHORT = 2
    INT = 3
    LONG = 4
    US_CHAR = 5
    US_SHORT = 6
    US_INT = 7
    US_LONG = 8

    integer_types = (CHAR, US_CHAR, SHORT, US_SHORT, INT, US_INT, LONG, US_LONG)
    signed_types = (US_CHAR, US_SHORT, US_INT, US_LONG)

    FLOAT = 9
    DOUBLE = 10

    # In array every element has identical type
    ARRAY_BEGIN = 11

    # In list there can be different types of elements
    LIST_BEGIN = 12

    STRING_BEGIN = 13

    names = (
        "END", 
        "CHAR",
        "SHORT",
        "INT",
        "LONG",
        "US_CHAR",
        "US_SHORT",
        "US_INT",
        "US_LONG",
        "FLOAT",
        "DOUBLE",
        "ARRAY_BEGIN",
        "LIST_BEGIN",
        "STRING_BEGIN",
        "NONE"
    )

    NONE = 14

    size_dict = {
        CHAR: 1,
        US_CHAR: 1,
        SHORT: 2,
        US_SHORT: 2,
        INT: 4,
        US_INT: 4,
        LONG: 8,
        US_LONG: 8,
        FLOAT: 4,
        DOUBLE: 8,
        NONE: 0
    }

def abs(x):
    if x < 0: x*=-1
    return x

def binary(x):
    return "0" * ((2 - len(bin(x))) % 8) + bin(x).removeprefix("0b") 

Stop = "\n" # TODO BUG THIS IS SO FUCKED...


class Serializator:

    @staticmethod
    def encode_to(obj: int|float|tuple|list|set|str, serialization_type: int, *args: list[int]):
        if serialization_type == SerializationTypes.NONE:
            if obj is not None:
                raise TypeError(f"{obj} is not None to be serialized as {SerializationTypes.names[serialization_type]}")
            return bytes([serialization_type])
        elif serialization_type in (SerializationTypes.US_CHAR, SerializationTypes.US_SHORT, SerializationTypes.US_INT, SerializationTypes.US_LONG):
            if not isinstance(obj, int):
                raise TypeError(f"{obj} is not integer to be serialized as {SerializationTypes.names[serialization_type]}")
            if obj < 0 or  obj > 256 ** SerializationTypes.size_dict[serialization_type]:
                raise ValueError(f"{obj} can not be serialized as {SerializationTypes.names[serialization_type]}")
            return bytes([serialization_type] + [(obj // (256 ** (SerializationTypes.size_dict[serialization_type] - i - 1))) % 256 for i in range(SerializationTypes.size_dict[serialization_type])])
        elif serialization_type in (SerializationTypes.CHAR, SerializationTypes.SHORT, SerializationTypes.INT, SerializationTypes.LONG):
            if abs(obj) > 256 ** SerializationTypes.size_dict[serialization_type] / 2:
                raise TypeError(f"{obj} can not be serialized as {SerializationTypes.names[serialization_type]}")
            obj %= 256 ** SerializationTypes.size_dict[serialization_type]
            return bytes([serialization_type] + [(obj // (256 ** (SerializationTypes.size_dict[serialization_type] - i - 1))) % 256 for i in range(SerializationTypes.size_dict[serialization_type])])
        elif serialization_type in (SerializationTypes.FLOAT, SerializationTypes.DOUBLE):
            if not isinstance(obj, float|int):
                raise TypeError(f"{obj} is not a real number to be serialized as {SerializationTypes.names[serialization_type]}")
            if obj == 0:
                return bytes(SerializationTypes.size_dict[serialization_type])
            result = bytearray(SerializationTypes.size_dict[serialization_type] + 1)
            result[0] = serialization_type
            exp = 127
            sign = obj > 0
            obj = abs(obj)
            if abs(obj) >= 2:
                exp += int(abs(obj)).bit_length() - 1
                obj /= (2 ** (int(abs(obj)).bit_length() - 1))
            elif abs(obj) < 1:
                exp -= int(abs(1/obj)).bit_length()
                obj *= 2 ** int(abs(1/obj)).bit_length()
                
            if exp > 255 or exp < 0:
                raise ValueError(f"{obj} is too big or too small to be serialized... wtf are you doing?")
            result[1] = exp
            obj -= 1
            obj /= 2
            for i in range(1, SerializationTypes.size_dict[serialization_type]):
                result[i + 1] = int((obj * (256 ** i))) % 256
            result[2] = (128 * int(not sign)) + (result[2] % 128)
            return bytes(result)
        elif serialization_type == SerializationTypes.ARRAY_BEGIN:
            if not isinstance(obj, tuple|list|set):
                raise TypeError(f"{obj} is not a set nor tuple nor list to be serialized as {SerializationTypes.names[serialization_type]}")
            result = bytearray((serialization_type, args[0]) + Serializator.encode_to(len(obj), SerializationTypes.INT))
            for inner in obj:
                result.extend(Serializator.encode_to(inner, args[0], args[1:])[1:])
            result.append(SerializationTypes.END)
            return result
        elif serialization_type == SerializationTypes.LIST_BEGIN:
            if not isinstance(obj, tuple|list|set):
                raise TypeError(f"{obj} is not a set nor tuple nor list to be serialized as {SerializationTypes.names[serialization_type]}")
            result = bytearray(serialization_type.to_bytes())
            for inner in obj:
                result.extend(Serializator.encode(inner))
            result.append(SerializationTypes.END)
            return result
        elif serialization_type == SerializationTypes.STRING_BEGIN:
            if not isinstance(obj, tuple|list|set|str):
                raise TypeError(f"{obj} is not a set nor tuple nor list to be serialized as {SerializationTypes.names[serialization_type]}")
            result = bytearray(serialization_type.to_bytes())
            if isinstance(obj, str):
                result.extend(obj.encode())
            else:
                for inner in obj:
                    result.extend(Serializator.encode_to(inner, SerializationTypes.US_CHAR)[1:])
            result.append(SerializationTypes.END)
            return result
        else:
            raise ValueError(f"Unknown serialization type {serialization_type} for {obj}")
    @staticmethod    
    def encode(obj: Any):
        if isinstance(obj, int):
            if obj > 0:
                if obj < 256:
                    return Serializator.encode_to(obj, SerializationTypes.US_CHAR)
                elif obj < 256**2:
                    return Serializator.encode_to(obj, SerializationTypes.US_SHORT)
                elif obj < 256**4:
                    return Serializator.encode_to(obj, SerializationTypes.US_INT)
                elif obj < 256**8:
                    return Serializator.encode_to(obj, SerializationTypes.US_LONG)
                else:
                    raise ValueError(f"{obj} is too big to be serialized... wtf are you doing?")
            else:
                if abs(obj) < 256**1 / 2:
                    return Serializator.encode_to(obj, SerializationTypes.CHAR)
                elif abs(obj) < 256**2 / 2:
                    return Serializator.encode_to(obj, SerializationTypes.SHORT)
                elif abs(obj) < 256**4 / 2:
                    return Serializator.encode_to(obj, SerializationTypes.INT)
                elif abs(obj) < 256**8 / 2:
                    return Serializator.encode_to(obj, SerializationTypes.LONG)
                else:
                    raise ValueError(f"{obj} is too big or too small to be serialized... wth are you doing?")
        if isinstance(obj, float):
            if obj.is_integer():
                return Serializator.encode(int(obj))
            return Serializator.encode_to(obj, SerializationTypes.FLOAT)
        if isinstance(obj, tuple|list|set):
            return Serializator.encode_to(obj, SerializationTypes.LIST_BEGIN)
        if isinstance(obj, str):
            return Serializator.encode_to(obj, SerializationTypes.STRING_BEGIN)
        if obj is None:
            return bytes([SerializationTypes.NONE])
        raise TypeError(f"{obj} is not serializable, please use int, float, str, list, tuple, set, or None")

    @staticmethod
    def decode_full(obj: bytes|bytearray):
        if int(obj[0]) in SerializationTypes.integer_types:
            result = 0
            for i in range(len(obj[1:])):
                result += int(obj[len(obj[1:]) - i]) * 256 ** i
            if not (int(obj[0]) in SerializationTypes.signed_types):
                if result >= 256 ** SerializationTypes.size_dict[int(obj[0])] / 2:
                    result -= 256 ** SerializationTypes.size_dict[int(obj[0])]
            return result
        if int(obj[0]) in (SerializationTypes.FLOAT, SerializationTypes.DOUBLE):
            exp = int(obj[1]) - 127
            
            sign = int(obj[2]) // 128
            result = 0

            for i in range(len(obj[2:])):
                result += int(obj[len(obj[2:]) - i + 1]) * 256 ** i
            
            if sign:
                result -= 256 ** (SerializationTypes.size_dict[int(obj[0])] - 1) / 2
                result *= -1
            result *= 2
            result /= 256 ** (SerializationTypes.size_dict[int(obj[0])] - 1)
            result += 1
            result *= 2 ** exp
            return result
        if int(obj[0]) == SerializationTypes.NONE:
            return None
        if int(obj[0]) in (SerializationTypes.ARRAY_BEGIN, SerializationTypes.LIST_BEGIN, SerializationTypes.STRING_BEGIN):
            result = []
            i = 1
            if int(obj[0]) == SerializationTypes.ARRAY_BEGIN:
                i += 1
            while obj[i] != SerializationTypes.END:
                if int(obj[0]) == SerializationTypes.LIST_BEGIN:
                    serialization_type = obj[i]
                    i += 1
                elif int(obj[0]) == SerializationTypes.ARRAY_BEGIN:
                    serialization_type = obj[1]
                elif int(obj[0]) == SerializationTypes.STRING_BEGIN:
                    serialization_type = SerializationTypes.US_CHAR
                
                if serialization_type in (SerializationTypes.ARRAY_BEGIN, SerializationTypes.LIST_BEGIN) :
                    result.append(Serializator.decode_full(serialization_type.to_bytes() + obj[i:]))
                    cnt = 1
                    while True:
                        if obj[i] == SerializationTypes.END:
                            cnt -= 1
                            if cnt == 0:
                                i += 1
                                break
                            i += 1
                        elif obj[i] == SerializationTypes.LIST_BEGIN:
                            cnt += 1
                            i += 1
                        elif obj[i] == SerializationTypes.STRING_BEGIN:
                            while obj[i] != SerializationTypes.END:
                                i += 1
                            i += 1
                        else:
                            i += SerializationTypes.size_dict[obj[i]] + 1
                elif serialization_type == SerializationTypes.STRING_BEGIN:
                    result.append(Serializator.decode_full(serialization_type.to_bytes() + obj[i:]))
                    while obj[i] != SerializationTypes.END:
                        i += 1
                    i += 1
                else:
                    result.append(Serializator.decode_full(serialization_type.to_bytes() + obj[i : i + SerializationTypes.size_dict[serialization_type]]))
                    i += SerializationTypes.size_dict[serialization_type]
                
            if int(obj[0]) == SerializationTypes.STRING_BEGIN:
                return bytes(result).decode()
            else:
                return result
            
    @staticmethod
    def decode_with_batching(conn: socket.socket):
        result = Stop
        typ = conn.recv(1)
        if len(typ) == 0:
            print("CONNECTION LOST")
            exit()
        if typ[0] == SerializationTypes.END:
            return Stop
        elif typ[0] in SerializationTypes.size_dict:
            if SerializationTypes.size_dict[typ[0]] != 0:
                recv = conn.recv(SerializationTypes.size_dict[typ[0]])
            else:
                recv = bytes()
            return Serializator.decode_full(typ + recv)
        elif typ[0] == SerializationTypes.STRING_BEGIN:
            result = bytearray()
            while True:
                recv = conn.recv(1)
                if recv[0] == SerializationTypes.END:
                    break    
                result.append(recv[0])
            return result.decode()
        elif typ[0] == SerializationTypes.LIST_BEGIN:
            result = []
            while True:
                next_element = Serializator.decode_with_batching(conn)
                if next_element == Stop:
                    break
                else:
                    result.append(next_element)
            return result
        else:
            raise ValueError(f"Unknown serialization type {typ[0]}")

def flags_to_int(*flags: tuple[bool]) -> int:
    result = 0
    for i in range(len(flags)):
        result += int(flags[i]) * (2 ** i)

    return result

def int_to_flags(integer: int, length: int) -> tuple[bool]:
    result = []
    while length != 0:
        length -= 1
        if integer % 2 == 0:
            result.append(False)
            integer //= 2
        else:
            result.append(True)
            integer -= 1
            integer //= 2
    
    return tuple(result)