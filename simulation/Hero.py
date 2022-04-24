import numpy as np
from GameEntity import GameEntity
from Player import Player
from ActionType import ActionType


class Hero(GameEntity):
    index: int
    owner: Player
    rotation: float
    intent: ActionType

    def __init__(self, index: int, position: np.ndarray, owner: Player, rotation: float) -> None:
        super().__init__(position, owner.getIndex())
        self.index = index
        self.owner = owner
        self.rotation = rotation
        self.intent = ActionType.IDLE

    def getOwner(self) -> Player:
        return self.owner

    def __repr__(self) -> str:
        return "Hero(id={}, position={}, owner={})".format(self.id, self.position, self.owner.index)
