from engine_antiantilopa import Vector2d

def find_annotation(cls: type, key: str):
    if key in cls.__annotations__:
        return cls.__annotations__[key]
    for base in cls.__bases__:
        res = find_annotation(base, key)
        if res is not None:
            return res
    return None

class Serializable:
    serialized_fields: list[str] = []

    @classmethod
    def from_serializable(cls, data: tuple, _cls = None):
        if _cls is None:
            a = cls.__new__(cls)
            for i, key in enumerate(cls.serialized_fields):
                attr_cls = find_annotation(cls, key)
                if attr_cls is not None:
                    if issubclass(attr_cls, Serializable):
                        object.__setattr__(a, key, attr_cls.from_serializable(data[i]))
                        continue
                    elif issubclass(type(attr_cls()), (list, tuple)):
                        object.__setattr__(a, key, Serializable.from_serializable(data[i], _cls=attr_cls))
                        continue
                else:
                    raise Exception(f"{key} field of {cls} is not annotated")
                object.__setattr__(a, key, data[i])
            return a
        else:
            assert issubclass(type(_cls()), (list, tuple))
            if issubclass(type(_cls()), list):
                if hasattr(_cls, "__args__"):
                    typ = _cls.__args__[0]
                else:
                    return data
                if issubclass(typ, Serializable):
                    result = []
                    for i in range(len(data)):
                        result.append(typ.from_serializable(data[i]))
                    return result
                elif issubclass(typ, (list, tuple)):
                    result = []
                    for i in range(len(data)):
                        result.append(Serializable.from_serializable(data[i], _cls=typ))
                    return result
                else:
                    return data
            elif issubclass(type(_cls()), tuple):
                if hasattr(_cls, "__args__"):
                    typs = _cls.__args__
                else:
                    return data
                result = []
                for i in range(len(data)):
                    if issubclass(typs[i], Serializable):
                        result.append(typs[i].from_serializable(data[i]))
                    elif issubclass(typ, (list, tuple)):
                        result.append(Serializable.from_serializable(data[i], _cls=typs[i]))
                    else:
                        result.append(data[i])
                return result

    def to_serializable(self) -> tuple:
        data = []
        for key in self.__class__.serialized_fields:
            value = getattr(self, key)

            if isinstance(value, (int, str, bool, float, Vector2d, list, tuple)):
                data.append(to_ser(value))
                continue
            if value is None:
                data.append(None)
                continue
            assert isinstance(value, Serializable), f"Field should be instance of Serializable, not {type(value).__name__}"
            data.append(value.to_serializable())
        return list(data)
    

# ACTUALLY BULLSHIT!!! REDO THIS AND RENAME. ONLY TEMPORARY SOLUTION!!! TODO
def to_ser(smth):
    if isinstance(smth, (int, str, bool, float, Vector2d)):
        return smth
    elif smth is None: 
        return None
    elif isinstance(smth, (list, tuple)):
        res = []
        for i in smth:
            res.append(to_ser(i))
        return res
    elif isinstance(smth, Serializable):
        return smth.to_serializable()
    
