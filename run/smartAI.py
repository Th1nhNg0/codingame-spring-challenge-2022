from collections import namedtuple
import math
import numpy as np
from stable_baselines3 import PPO
import random
import os
import sys
import time
Entity = namedtuple('Entity', [
    'id', 'type', 'x', 'y', 'shieldLife', 'isControlled', 'health', 'vx', 'vy', 'nearBase', 'threatFor',
])

model = PPO.load("run/models/1650928992/500000.zip")


def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def point_on_circle(x0, y0, radius, angle):
    x = x0 + radius * math.cos(angle)
    y = y0 + radius * math.sin(angle)
    return int(x), int(y)


def in_range(monster_x, monster_y, x, y, radius):
    return distance(monster_x, monster_y, x, y) <= radius


def get_guard_position(x, y, radius):
    pos = []
    for i in range(12):
        angle = 2 * math.pi / 12 * (0.5+i)
        x_, y_ = point_on_circle(x, y, radius, angle)
        if x_ < 0 or y_ < 0 or x_ > MAP_WIDTH or y_ > MAP_HEIGHT:
            continue
        pos.append((x_, y_))
    return pos


def predict_hero_move(hero, cmd):
    if "MOVE" not in cmd:
        return hero.x, hero.y
    cmdx, cmdy = map(int, cmd.split(" ")[1:])
    # max length is 800
    if distance(hero.x, hero.y, cmdx, cmdy) <= 800:
        return cmdx, cmdy
    else:
        angle = math.atan2(cmdy - hero.y, cmdx - hero.x)
        return int(hero.x + 800 * math.cos(angle)), int(hero.y + 800 * math.sin(angle))


TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2


MAP_WIDTH, MAP_HEIGHT = 17630, 9000
# base_x,base_y: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]

opponent_base_x, opponent_base_y = MAP_WIDTH-base_x, MAP_HEIGHT-base_y


heroes_per_player = int(input())

attack_on = False

wild_mana = 0

last_turn_mana = 0
last_turn_wild_mana = 0
last_turn_my_health = 3
last_turn_op_health = 3

first_turn = True
# game loop
while True:
    my_health, my_mana = [int(j) for j in input().split()]
    enemy_health, enemy_mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

    monsters: list[Entity] = []
    my_heroes: list[Entity] = []
    opp_heroes: list[Entity] = []
    for i in range(entity_count):
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [
            int(j) for j in input().split()]
        entity = Entity(
            _id,            # _id: Unique identifier
            _type,          # _type: 0=monster, 1=your hero, 2=opponent hero
            x, y,           # x,y: Position of this entity
            shield_life,    # shield_life: Ignore for this league; Count down until shield spell fades
            is_controlled,  # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
            health,         # health: Remaining health of this monster
            vx, vy,         # vx,vy: Trajectory of this monster
            near_base,      # near_base: 0=monster with no target yet, 1=monster targeting a base
            threat_for,      # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        )

        if _type == TYPE_MONSTER:
            monsters.append(entity)
        elif _type == TYPE_MY_HERO:
            my_heroes.append(entity)
        elif _type == TYPE_OP_HERO:
            opp_heroes.append(entity)

    # calc reward:
    reward = 0
    if my_health < last_turn_my_health:
        reward += (my_health-last_turn_my_health)*1000
    if enemy_health < last_turn_op_health:
        reward += -(enemy_health-last_turn_op_health)*1000
    reward += my_mana-last_turn_mana
    reward += 5*last_turn_wild_mana

    state = [my_health,
             my_mana,
             enemy_health,
             enemy_mana
             ]
    for hero in my_heroes:
        state.extend(list(hero))
    for i in range(heroes_per_player):
        if i < len(opp_heroes):
            state.extend(list(opp_heroes[i]))
        else:
            state.extend([-1]*11)
    for i in range(20):
        if i < len(monsters):
            state.extend(list(monsters[i]))
        else:
            state.extend([-1]*11)

    data = {
        'state': state,
        'reward': reward,
        'action': None
    }

    last_turn_wild_mana = wild_mana
    last_turn_mana = my_mana
    last_turn_my_health = my_health
    last_turn_op_health = enemy_health

    actions, _ = model.predict(observation=np.array(state))
    '''
    0: Move to defend position
    1: Move to hero's nearest monster
    2: Move to base's nearest monster
    3: Move to opponent base at random position x,y in [5000,5000] from base
    4: Move to hero's nearest opponent hero
    5: Move to hero's farthest opponent hero

    6: Spell Shield on self
    7: Spell Shielf on nearest monster in hero range
    8: Spell Shielf on farthest monster in hero range

    9: Spell wind to opponent base

    10: Control nearest monster to opponent base of map in hero range
    11: Control farthest monster to opponent base of map in hero range
    12: Control nearest opponent hero to middle map in hero range
    13: Control farthest opponent hero to middle map in hero range
    '''
    cmds = [
        'WAIT',
        'WAIT',
        'WAIT'
    ]

    for index, action in enumerate(actions):
        hero = my_heroes[index]
        if action == 0:
            x, y = get_guard_position(base_x, base_y, 6200)[index]
            cmds[index] = f'MOVE {x} {y}'

        if action == 1:
            nearest_monster = None
            nearest_distance = 1e18
            for m in monsters:
                d = distance(hero.x, hero.y, m.x, m.y)
                if d < nearest_distance:
                    nearest_monster = m
                    nearest_distance = d
            if nearest_monster is not None:
                cmds[index] = f'MOVE {nearest_monster.x+nearest_monster.vx} {nearest_monster.y+nearest_monster.vy}'

        if action == 2:
            nearest_monster = None
            nearest_distance = 1e18
            for m in monsters:
                d = distance(hero.x, hero.y, m.x, m.y)
                if d < nearest_distance:
                    nearest_monster = m
                    nearest_distance = d
            if nearest_monster is not None:
                cmds[index] = f'MOVE {nearest_monster.x+nearest_monster.vx} {nearest_monster.y+nearest_monster.vy}'

        if action == 3:
            x = random.randint(0, 5001)
            y = random.randint(0, 5001)
            if opponent_base_x != 0:
                x = opponent_base_x-x
                y = opponent_base_y-y
            cmds[index] = f'MOVE {x} {y}'

        if action == 4:
            nearest_hero = None
            nearest_distance = 1e18
            for h in opp_heroes:
                d = distance(hero.x, hero.y, h.x, h.y)
                if d < nearest_distance:
                    nearest_hero = h
                    nearest_distance = d
            if nearest_hero is not None:
                cmds[index] = f'MOVE {nearest_hero.x} {nearest_hero.y}'

        if action == 5:
            farthest_hero = None
            farthest_distance = 0
            for h in opp_heroes:
                d = distance(hero.x, hero.y, h.x, h.y)
                if d > farthest_distance:
                    farthest_hero = h
                    farthest_distance = d
            if farthest_hero is not None:
                cmds[index] = f'MOVE {farthest_hero.x} {farthest_hero.y}'

        if action == 6:
            if my_mana >= 10:
                cmds[index] = f'SPELL SHIELD {hero.id}'

        if action == 7:
            if my_mana >= 10:
                nearest_monster = None
                nearest_distance = 1e18
                for m in monsters:
                    d = distance(hero.x, hero.y, m.x, m.y)
                    if d < nearest_distance:
                        nearest_monster = m
                        nearest_distance = d
                if nearest_monster is not None and in_range(hero.x, hero.y, nearest_monster.x, nearest_monster.y, 2200):
                    cmds[index] = f'SPELL SHIELD {nearest_monster.id}'

        if action == 8:
            if my_mana >= 10:
                farthest_monster = None
                farthest_distance = 0
                for m in monsters:
                    d = distance(hero.x, hero.y, m.x, m.y)
                    if d > farthest_distance:
                        farthest_monster = m
                        farthest_distance = d
                if farthest_monster is not None and in_range(hero.x, hero.y, farthest_monster.x, farthest_monster.y, 2200):
                    cmds[index] = f'SPELL SHIELD {farthest_monster.id}'

        if action == 9:
            if my_mana >= 10:
                cmds[index] = f'SPELL WIND {opponent_base_x} {opponent_base_y}'

        if action == 10:
            if my_mana >= 10:
                nearest_monster = None
                nearest_distance = 1e18
                for m in monsters:
                    d = distance(hero.x, hero.y, m.x, m.y)
                    if d < nearest_distance:
                        nearest_monster = m
                        nearest_distance = d
                if nearest_monster is not None and in_range(hero.x, hero.y, nearest_monster.x, nearest_monster.y, 2200):
                    cmds[index] = f'SPELL CONTROL {nearest_monster.id} {opponent_base_x} {opponent_base_y}'

        if action == 11:
            if my_mana >= 10:
                farthest_monster = None
                farthest_distance = 0
                for m in monsters:
                    d = distance(hero.x, hero.y, m.x, m.y)
                    if d > farthest_distance:
                        farthest_monster = m
                        farthest_distance = d
                if farthest_monster is not None and in_range(hero.x, hero.y, farthest_monster.x, farthest_monster.y, 2200):
                    cmds[index] = f'SPELL CONTROL {farthest_monster.id} {opponent_base_x} {opponent_base_y}'

        if action == 12:
            if my_mana >= 10:
                nearest_hero = None
                nearest_distance = 1e18
                for h in opp_heroes:
                    d = distance(hero.x, hero.y, h.x, h.y)
                    if d < nearest_distance:
                        nearest_hero = h
                        nearest_distance = d
                if nearest_hero is not None and in_range(hero.x, hero.y, nearest_hero.x, nearest_hero.y, 2200):
                    cmds[index] = f'SPELL CONTROL {nearest_hero.id} {MAP_WIDTH//2} {MAP_HEIGHT//2}'

        if action == 13:
            if my_mana >= 10:
                farthest_hero = None
                farthest_distance = 0
                for h in opp_heroes:
                    d = distance(hero.x, hero.y, h.x, h.y)
                    if d > farthest_distance:
                        farthest_hero = h
                        farthest_distance = d
                if farthest_hero is not None and in_range(hero.x, hero.y, farthest_hero.x, farthest_hero.y, 2200):
                    cmds[index] = f'SPELL CONTROL {farthest_hero.id} {MAP_WIDTH//2} {MAP_HEIGHT//2}'

        if "SPELL" in cmds[index]:
            my_mana -= 10

        # compute wild mana
        new_x, new_y = predict_hero_move(hero, cmds[index])
        for m in monsters:
            if in_range(new_x, new_y, m.x, m.y, 800) and distance(m.x, m.y, base_x, base_y) > 5000:
                wild_mana += 2
                last_turn_wild_mana += 2

        cmds[index] += f' {action}'

    first_turn = False

    for cmd in cmds:
        print(cmd)
