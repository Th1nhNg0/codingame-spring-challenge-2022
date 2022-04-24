from GameEntity import GameEntity
import numpy as np
import Configuration


class Mob(GameEntity):

    def __init__(self, position: np.ndarray, health: int) -> None:
        super().__init__(position, Configuration.TYPE_MOB)
        self.speed = np.array([0, 0])
        self.health = health
        self.pushed = False
        self.nextControls = np.array([])
        self.healthChanged = True

    def isAlive(self) -> bool:
        return self.health > 0

    def hit(self, damage: int) -> None:
        self.health -= damage
        self.healthChanged = True

    def getHealth(self) -> int:
        return self.health

    def healthHasChanged(self) -> bool:
        return self.healthChanged

    def moveCancelled(self) -> bool:
        return not self.isAlive() or self.pushed

    def setSpeed(self, speed: np.ndarray) -> None:
        self.speed = speed
        self.status = None

    def getSpeed(self) -> np.ndarray:
        return self.speed

    def resetSpeed(self) -> None:
        self.pushed = False
        self.healthChanged = False
        self.activeControls = self.nextControls.copy()
        self.nextControls = np.array([])

    def getOwner(self):
        return None

    def pushTo(self, position: np.ndarray) -> None:
        super().pushTo(position)
        self.pushed = True
        self.status = None
