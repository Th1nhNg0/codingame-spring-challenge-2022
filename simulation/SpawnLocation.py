import numpy as np
import Configuration


class SpawnLocation:
    def __init__(self, x, y):
        self.position = np.array([x, y])
        self.symetry = np.array([
            Configuration.MAP_WIDTH - x, Configuration.MAP_HEIGHT - y])
        self.direction = np.array(
            [0, 1 if self.position[1] <= Configuration.MAP_HEIGHT / 2 else -1])
