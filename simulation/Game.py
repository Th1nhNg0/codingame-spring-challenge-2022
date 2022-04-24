import math
from typing import Union
import Configuration
from MobSpawner import MobSpawner

from Player import Player
from ActionType import ActionType
from Hero import Hero
from Mob import Mob
from MobSpawner import MobSpawner
from Vector import Vector
import random as randomLib
from GameEntity import GameEntity


class Game:
    TYPE_MY_HERO = 0
    TYPE_ENEMY_HERO = 1
    TYPE_MOB = 2
    INPUT_TYPE_MOB = 0
    INPUT_TYPE_MY_HERO = 1
    INPUT_TYPE_ENEMY_HERO = 2

    playerCount: int
    seed: int
    random: randomLib.Random
    allHeroes: list[Hero] = []
    allMobs: list[Mob] = []
    mobRemovals = set()
    mobSpawner: MobSpawner
    newEntities: list[GameEntity] = []
    # private List < Attack > attacks = new ArrayList <> ()
    # private List < SpellUse > spellUses = new ArrayList <> ()
    # private List < BaseAttack > baseAttacks = new ArrayList <> ()
    # private Map < ActionType, List < Hero >> intentMap = new HashMap <> ()
    # private Map < Set < Vector > , Double > positionKeyMap = new HashMap <> ()

    players = []
    intentMap = {}
    corners = [Vector(0, 0),
               Vector(Configuration.MAP_WIDTH, Configuration.MAP_HEIGHT)]
    startDirections = [
        Vector(1, 1).normalize(),
        Vector(-1, -1).normalize()
    ]
    basePositions = []
    symmetryOrigin: Vector

    @property
    def allEntities(self):
        return self.allHeroes + self.allMobs

    def __init__(self) -> None:

        self.MAX_TURN = Configuration.MAX_TURN
        self.symmetryOrigin = (Configuration.MAP_WIDTH/2,
                               Configuration.MAP_HEIGHT/2)

        self.seed = randomLib.randint(0, 1000000)
        self.random = randomLib.Random(self.seed)

        self.mobSpawner = MobSpawner(
            self.random,
            Configuration.MOB_SPAWN_LOCATIONS,
            Configuration.MOB_SPAWN_MAX_DIRECTION_DELTA,
            Configuration.MOB_SPAWN_RATE
        )

        for action in ActionType:
            self.intentMap[action] = []
        self.initPlayers()

    def snapToGameZone(self, v):
        snapX = v.getX()
        snapY = v.getY()

        if (snapX < 0):
            snapX = 0
        if (snapX >= Configuration.MAP_WIDTH):
            snapX = Configuration.MAP_WIDTH - 1
        if (snapY < 0):
            snapY = 0
        if (snapY >= Configuration.MAP_HEIGHT):
            snapY = Configuration.MAP_HEIGHT - 1
        return Vector(snapX, snapY)

    def initPlayers(self):
        spawnOffset = 1600
        spaceBetweenHeroes = 400
        for i in range(2):
            player = Player(i)
            vector = (Vector(1, -1) if i < 2 else Vector(1, 1)).normalize()
            if i % 2 == 1:
                vector = vector.mult(-1)

            startPoint = self.corners[i]
            self.basePositions.append(startPoint)
            offsets = [0, 1, -1, 2, -2, 3, -3, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for j in range(Configuration.HEROES_PER_PLAYER):
                offset = offsets[j + (1 - Configuration.HEROES_PER_PLAYER % 2)]

                position = vector.mult(offset * (spaceBetweenHeroes)).add(
                    startPoint).add(self.startDirections[i].mult(spawnOffset)).round()

                position = self.snapToGameZone(position)

                hero = Hero(j, position, player,
                            self.startDirections[i].angle())
                player.addHero(hero)
                self.allHeroes.append(hero)
                self.newEntities.append(hero)
