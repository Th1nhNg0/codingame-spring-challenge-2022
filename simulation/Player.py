import Configuration


class Player:
    heroes = []
    mana = Configuration.STARTING_MANA
    manaChanged = True
    baseHealthChanged = True
    baseHealth = Configuration.STARTING_BASE_HEALTH
    spotted = set()
    manaGainedOutsideOfBase = 0
    index = 0

    def __init__(self, index) -> None:
        self.index = index

    def getExpectedOutputLines(self):
        return len(self.heroes)

    def addHero(self, hero):
        self.heroes.append(hero)

    def gainMana(self, amount: list):
        self.mana += amount[0]
        self.manaGainedOutsideOfBase += amount[1]
        if (Configuration.MAX_MANA > 0):
            if (self.mana > Configuration.MAX_MANA):
                self.mana = Configuration.MAX_MANA
            if (self.manaGainedOutsideOfBase > Configuration.MAX_MANA):
                self.manaGainedOutsideOfBase = Configuration.MAX_MANA
        self.manaChanged = True

    def getMana(self):
        return self.mana

    def manaHasChanged(self):
        return self.manaChanged

    def resetViewData(self):
        self.manaChanged = False
        self.baseHealthChanged = False

    def spendMana(self, amount):
        self.mana -= amount
        self.manaChanged = True

    def getBaseHealth(self):
        return self.baseHealth

    def getManaGainedOutsideOfBase(self):
        return self.manaGainedOutsideOfBase

    def damageBase(self):
        self.baseHealth -= 1
        if (self.baseHealth < 0):
            self.baseHealth = 0
        self.baseHealthChanged = True

    def baseHealthHasChanged(self):
        return self.baseHealthChanged

    def getIndex(self) -> int:
        return self.index
