from typing import TypeVar
import json
from ..generic_types import GenericType

T = TypeVar("T", bound=GenericType)

def to_cls(cls: type, data: dict):
    new = cls.__new__(cls)

    if '__annotations__' in vars(cls).keys():
        variables = vars(cls)['__annotations__']
        for i, j in data.items():
            if i in variables:
                if variables[i] in (str, int, bool, list, tuple, dict):
                    new.__setattr__(i, j)
                else:
                    new.__setattr__(i, variables[i])
    return new

def from_file(tp: type[T], path: str) -> T:
   obj_json = json.load(open(path))
   return tp(**obj_json)