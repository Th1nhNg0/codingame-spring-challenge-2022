from enum import Enum, auto


class ActionType(Enum):
    MOVE = auto()
    WIND = auto()
    SHIELD = auto()
    CONTROL = auto()
    IDLE = auto()
