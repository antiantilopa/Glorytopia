from pygame_tools_tafh import Vector2d

class Serializable:
    serialized_fields: list[str] = []

    @classmethod
    def from_serializable(cls, data: tuple):
        a = cls.__new__(cls)
        for i, key in enumerate(cls.serialized_fields):
            setattr(a, key, data[i])
        return a

    def to_serializable(self) -> tuple:
        data = []
        for key in self.__class__.serialized_fields:
            value = getattr(self, key)

            if isinstance(value, (int, str, bool, float, list, tuple)):
                data.append(value)
                continue
            
            if isinstance(value, Vector2d):
                data.append(value.as_tuple())
                continue
            
            assert isinstance(value, Serializable), "Field should be instance of Serializable to serialize"
            data.append(value.to_serializable())
        return tuple(data)
