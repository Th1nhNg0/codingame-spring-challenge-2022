from SpawnLocation import SpawnLocation
import Configuration
from Mob import Mob
import numpy as np


class MobSpawner:
    currentMaxHealth = Configuration.MOB_STARTING_MAX_ENERGY

    def __init__(self, random: np.random.RandomState, spawnLocations: list[SpawnLocation], maxDirectionDelta: float, spawnRate: int):
        self.random = random
        self.spawnLocations = spawnLocations
        self.maxDirectionDelta = maxDirectionDelta
        self.spawnRate = spawnRate

        self.lastSpawn = -spawnRate

    def update(self, turn: int):
        suddenDeath = turn >= 200

        if (turn - self.lastSpawn >= self.spawnRate):
            self.lastSpawn = turn
            return self.spawn(suddenDeath)
        return []

    def opposite(self, v: np.ndarray):
        return np.array(Configuration.MAP_WIDTH - v[0], Configuration.MAP_HEIGHT - v[1])

    def spawn(self, suddenDeath: bool):
        newMobs = []

        for pairToUse in self.spawnLocations:
            suddenDeathTarget = None

            if (suddenDeath):
                tx = self.random.randint(
                    0, Configuration.BASE_ATTRACTION_RADIUS)
                ty = self.random.randint(
                    0, Configuration.BASE_ATTRACTION_RADIUS)
                if (self.random.nextBoolean()):
                    tx = Configuration.MAP_WIDTH - tx
                    ty = Configuration.MAP_HEIGHT - ty
                suddenDeathTarget = np.array(tx, ty)

            directionDelta = self.random.random() * self.maxDirectionDelta * \
                2 - self.maxDirectionDelta
            for i in range(2):
                location = pairToUse.position if i == 0 else pairToUse.symetry
                direction = pairToUse.direction if i == 0 else pairToUse.direction.symmetric()
                mob = Mob(location,  self.currentMaxHealth)
                if (suddenDeath):
                    v = np.array([location,  suddenDeathTarget if i ==
                                 0 else self.opposite(suddenDeathTarget)])
                    v = v / np.linalg.norm(v) * Configuration.MOB_MOVE_SPEED
                    v = np.trunc(v)
                    mob.setSpeed(v)
                else:
                    v = direction.rotate(directionDelta)
                    v = v / np.linalg.norm(v) * Configuration.MOB_MOVE_SPEED
                    v = np.trunc(v)
                    mob.setSpeed(v)
                newMobs.add(mob)
        self.currentMaxHealth += Configuration.MOB_GROWTH_MAX_ENERGY
        return newMobs
