from abc import abstractmethod
import numpy as np
import Configuration


class GameEntity:
    ENTITY_COUNT = 0

    def __init__(self, position: np.ndarray, type: int) -> None:
        self.id = GameEntity.ENTITY_COUNT
        GameEntity.ENTITY_COUNT += 1
        self.position = position
        self.type = type
        self.activeControls = np.array([])
        self.shieldDuration = 0

    def getId(self) -> int:
        return self.id

    def applyControls(self, destination: np.ndarray) -> None:
        self.activeControls.append(destination)

    def applyShield(self) -> None:
        self.shieldDuration = Configuration.SPELL_PROTECT_DURATION + 1

    @abstractmethod
    def getOwner(self):
        pass

    def hasActiveShield(self) -> bool:
        return self.shieldDuration > 0 and self.shieldDuration < Configuration.SPELL_PROTECT_DURATION + 1

    def hadActiveShield(self) -> bool:
        return self.shieldDuration > 0 and self.shieldDuration < Configuration.SPELL_PROTECT_DURATION

    def gotPushed(self) -> bool:
        return self.pushed

    def isControlled(self) -> bool:
        return self.activeControls.size > 0

    def pushTo(self, position: np.ndarray) -> None:
        self.position = position

    def __repr__(self) -> str:
        return "GameEntity(id={}, position={}, type={})".format(self.id, self.position, self.type)
