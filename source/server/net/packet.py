from typing import TypeVar

T = TypeVar("T")

def serializer():
    """
    Example:

    @serializer
    class Data:
        
    """
    def wrapper(cls: type[T]):
        pass

    return wrapper