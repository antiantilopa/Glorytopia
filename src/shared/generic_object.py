from netio.serialization.serializer import Serializable
from netio.util.generic_type import GenericType

class GenericObject(Serializable):
    type: GenericType
