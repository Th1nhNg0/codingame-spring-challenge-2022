from cmath import pi
import sys
from collections import namedtuple
import math
import random

# print("Debug messages...", file=sys.stderr, flush=True)


Entity = namedtuple('Entity', [
    'id', 'type', 'x', 'y', 'shieldLife', 'isControlled', 'health', 'vx', 'vy', 'nearBase', 'threatFor',
])


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
        angle = 2 * pi / 12 * (0.5+i)
        x_, y_ = point_on_circle(x, y, radius, angle)
        if x_ < 0 or y_ < 0 or x_ > MAP_WIDTH or y_ > MAP_HEIGHT:
            continue
        pos.append((x_, y_))
    return pos


TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2


MAP_WIDTH, MAP_HEIGHT = 17630, 9000
# base_x,base_y: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]

opponent_base_x, opponent_base_y = MAP_WIDTH-base_x, MAP_HEIGHT-base_y


heroes_per_player = int(input())

attack_on = False

# game loop
while True:
    my_health, my_mana = [int(j) for j in input().split()]
    enemy_health, enemy_mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

    isMonsterTargeted = {}

    monsters = []
    my_heroes = []
    opp_heroes = []
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
            isMonsterTargeted[entity.id] = False
        elif _type == TYPE_MY_HERO:
            my_heroes.append(entity)
        elif _type == TYPE_OP_HERO:
            opp_heroes.append(entity)

    isHeroUsed = [False] * 3
    cmds = [
        None,
        None,
        None
    ]
    attacker_hero_id = 1

    if my_mana > 200:
        attack_on = True

    while True:
        best_action = None
        best_value = 0
        best_hero = None
        best_monster = None

        for i in range(heroes_per_player):
            if isHeroUsed[i]:
                continue
            hero = my_heroes[i]

            # move to guard position
            max_dist = 6200
            if attack_on:
                max_dist = 4500
            x, y = get_guard_position(base_x, base_y, max_dist)[i]
            value = 1e5
            if value > best_value:
                best_value = value
                best_hero = i
                best_monster = None
                if hero.x != x or hero.y != y:
                    best_action = f'MOVE {x} {y} moving to guard position'
                else:
                    best_action = f'WAIT HERO {i}'
            # use wind spell
            if my_mana >= 10:
                is_monster_near_base = False
                for m in monsters:
                    if in_range(m.x, m.y,  hero.x, hero.y, 1280) and m.shieldLife == 0 and m.health+3 > 2*distance(m.x, m.y, base_x, base_y)/400:
                        is_monster_near_base = True
                        break
                if is_monster_near_base:
                    value = 1e8
                    if value > best_value:
                        best_value = value
                        best_hero = i
                        best_monster = None
                        best_action = f'SPELL WIND {opponent_base_x} {opponent_base_y} cast wind spell'
            # farming
            for m in monsters:
                if isMonsterTargeted[m.id] or not in_range(m.x, m.y, base_x, base_y, 9000):
                    continue
                value = 1e6 - distance(m.x, m.y, hero.x, hero.y)
                if value > best_value:
                    best_value = value
                    best_hero = i
                    best_action = f'MOVE {m.x + m.vx} {m.y + m.vy } farming {m.id}'
                    best_monster = m

            # attack monster to defense
            for m in monsters:

                if isMonsterTargeted[m.id] or not ((m.nearBase == 1 and m.threatFor == 1) or (m.nearBase == 0 and m.threatFor == 1)):
                    continue
                value = 1e7 - distance(base_x, base_y, m.x,
                                       m.y) - distance(m.x, m.y, hero.x, hero.y)
                if value > best_value:
                    best_value = value
                    best_action = f'MOVE {m.x+m.vx} {m.y+m.vy} attacking {m.id}'
                    best_hero = i
                    best_monster = m

            # sabotage
            if attack_on and i == attacker_hero_id:
                # move attacker hero to opponent base
                random_radius = random.randint(1500, 6000)
                possible_pos = get_guard_position(
                    opponent_base_x, opponent_base_y, random_radius)
                target_x, target_y = random.choice(possible_pos)
                value = 1e9
                if value > best_value:
                    best_value = value
                    best_hero = i
                    best_action = f'MOVE {target_x} {target_y} moving to opponent base'
                    best_monster = None

                # always have 20 mana for defense
                if my_mana >= 30:
                    # use shield spell
                    for m in monsters:
                        if not ((m.nearBase == 1 and m.threatFor == 2) or (m.nearBase == 0 and m.threatFor == 2)):
                            continue
                        if m.shieldLife > 0 or distance(m.x, m.y, hero.x, hero.y) > 2200:
                            continue
                        if distance(m.x, m.y, opponent_base_x, opponent_base_y) > 5000:
                            continue
                        if m.health/2 < (distance(m.x, m.y, opponent_base_x, opponent_base_y) - 300)/400:
                            continue
                        value = 4e9
                        if value > best_value:
                            best_value = value
                            best_hero = i
                            best_action = f'SPELL SHIELD {m.id} shield {m.id}'
                            best_monster = None
                    # use wind spell
                    is_monster_near_base = 0
                    for m in monsters:
                        if in_range(m.x, m.y,  opponent_base_x, opponent_base_y, 5000+2200) and in_range(m.x, m.y,  hero.x, hero.y, 1280) and m.shieldLife == 0:
                            is_monster_near_base += 1
                    if is_monster_near_base >= 2:
                        value = 3e9
                        if value > best_value:
                            best_value = value
                            best_hero = i
                            best_monster = None
                            best_action = f'SPELL WIND {opponent_base_x} {opponent_base_y} cast wind spell'
                    # use control spell
                    for m in monsters:
                        if (m.nearBase == 1 and m.threatFor == 2) or (m.nearBase == 0 and m.threatFor == 2):
                            continue
                        if m.health < 15:
                            continue
                        if distance(m.x, m.y, hero.x, hero.y) > 2200 or distance(hero.x, hero.y, opponent_base_x, opponent_base_y) > 7000:
                            continue
                        if distance(m.x, m.y, opponent_base_x, opponent_base_y) < 5000:
                            continue
                        value = 2e9
                        if value > best_value:
                            best_value = value
                            best_hero = i
                            best_action = f'SPELL CONTROL {m.id} {opponent_base_x} {opponent_base_y} control {m.id}'
                            best_monster = None
                    # control opponent hero
                    for opponent_hero in opp_heroes:
                        if opponent_hero.shieldLife > 0:
                            continue
                        if not in_range(opponent_hero.x, opponent_hero.y, opponent_base_x, opponent_base_y, 5000):
                            continue
                        if not in_range(opponent_hero.x, opponent_hero.y, hero.x, hero.y, 2200):
                            continue
                        if_attack_monster = 0
                        for m in monsters:
                            if in_range(m.x, m.y, opponent_hero.x, opponent_hero.y, 800):
                                if_attack_monster += 1
                        if if_attack_monster > 0:
                            value = 5e9 + if_attack_monster
                            if value > best_value:
                                best_value = value
                                best_hero = i
                                best_action = f'SPELL CONTROL {opponent_hero.id} {MAP_WIDTH//2 } {MAP_HEIGHT//2} block {opponent_hero.id}'
                                best_monster = None
                    # wind opponent hero
                    for opponent_hero in opp_heroes:
                        if opponent_hero.shieldLife > 0:
                            continue
                        if not in_range(opponent_hero.x, opponent_hero.y, opponent_base_x, opponent_base_y, 5000):
                            continue
                        if not in_range(opponent_hero.x, opponent_hero.y, hero.x, hero.y, 1280):
                            continue
                        if_attack_monster = 0
                        for m in monsters:
                            if in_range(m.x, m.y, opponent_hero.x, opponent_hero.y, 800) and m.shieldLife > 0:
                                if_attack_monster += 1
                        if if_attack_monster > 0:
                            value = 6e9 + if_attack_monster
                            if value > best_value:
                                best_value = value
                                best_hero = i
                                best_action = f'SPELL WIND  {MAP_WIDTH//2 } {MAP_HEIGHT//2} cast wind spell'
                                best_monster = None
        if best_hero is None:
            break

        if best_monster is not None:
            isMonsterTargeted[best_monster.id] = True

        if 'SPELL' in best_action:
            my_mana -= 10

        isHeroUsed[best_hero] = True
        cmds[best_hero] = best_action

    for cmd in cmds:
        print(cmd)
