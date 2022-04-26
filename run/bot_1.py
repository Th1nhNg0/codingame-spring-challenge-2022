from collections import namedtuple
import math
import sys
import pickle
import random

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
    state.append(len(monsters))  # number of visible monster
    monster_in_range_base = 0
    for m in monsters:
        if in_range(m.x, m.y, base_x, base_y, 5000):
            monster_in_range_base += 1
    state.append(monster_in_range_base)

    for hero in my_heroes:
        monster_in_range_wind = 0
        monster_in_range_spell = 0
        monster_in_range_attack = 0
        for m in monsters:
            if in_range(m.x, m.y, hero.x, hero.y, 800):
                monster_in_range_attack += 1
            if in_range(m.x, m.y, hero.x, hero.y, 1280):
                monster_in_range_wind += 1
            if in_range(m.x, m.y, hero.x, hero.y, 2200):
                monster_in_range_spell += 1
        state.extend([hero.x, hero.y, hero.shieldLife, hero.isControlled,
                      monster_in_range_wind, monster_in_range_spell, monster_in_range_attack])

    for i in range(heroes_per_player):
        if i < len(opp_heroes):
            monster_in_range_wind = 0
            monster_in_range_spell = 0
            monster_in_range_attack = 0
            for m in monsters:
                if in_range(m.x, m.y, hero.x, hero.y, 800):
                    monster_in_range_attack += 1
                if in_range(m.x, m.y, hero.x, hero.y, 1280):
                    monster_in_range_wind += 1
                if in_range(m.x, m.y, hero.x, hero.y, 2200):
                    monster_in_range_spell += 1
            state.extend([opp_heroes[i].x, opp_heroes[i].y,
                         opp_heroes[i].shieldLife, opp_heroes[i].isControlled,
                         monster_in_range_wind, monster_in_range_spell, monster_in_range_attack])
        else:
            state.extend([-1, -1, -1, -1, -1, -1, -1])

    data = {
        'state': state,
        'reward': reward,
        'action': None
    }

    # data = {
    #     'state': {
    #         'my_health': my_health,
    #         'my_mana': my_mana,
    #         'enemy_health': enemy_health,
    #         'enemy_mana': enemy_mana,
    #         'monsters': monsters,
    #         'my_heroes': my_heroes,
    #         'opp_heroes': opp_heroes,
    #     },
    #     'reward': reward,
    #     'action': 1 if first_turn else None
    # }
    pickle.dump(data, open("data.p", "wb"))

    wait_for_action = True
    while wait_for_action:
        try:
            data = pickle.load(open("data.p", "rb"))
            if data['action'] is not None:
                wait_for_action = False
        except:
            pass

    last_turn_wild_mana = wild_mana
    last_turn_mana = my_mana
    last_turn_my_health = my_health
    last_turn_op_health = enemy_health

    actions = data['action']

    '''
    0: Move to defend position
    1: Move to hero's nearest monster
    2: Move to base's nearest monster
    3: Move to opponent base at random position x,y in [5000,5000] from base

    4: Spell Shield on self
    5: Spell Shielf on random monster in hero range

    6: Spell wind to opponent base

    7: Control random monster to opponent base of map in hero range
    8: Control random opponent hero to middle map in hero range

    9: WAIT for next turn
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
                d = distance(base_x,base_y, m.x, m.y)
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
            if my_mana >= 10:
                cmds[index] = f'SPELL SHIELD {hero.id}'

        if action == 5:
            if my_mana >= 10:
                monster_in_hero_range = [
                    m for m in monsters if in_range(m.x, m.y, hero.x, hero.y, 2200)]
                random_monster = random.choice(monster_in_hero_range)
                if random_monster is not None:
                    cmds[index] = f'SPELL SHIELD {random_monster.id}'

        if action == 6:
            if my_mana >= 10:
                cmds[index] = f'SPELL WIND {opponent_base_x} {opponent_base_y}'

        if action == 7:
            if my_mana >= 10:
                monster_in_hero_range = [
                    m for m in monsters if in_range(m.x, m.y, hero.x, hero.y, 2200)]
                random_monster = random.choice(monster_in_hero_range)
                if random_monster is not None:
                    cmds[index] = f'SPELL CONTROL {random_monster.id} {opponent_base_x} {opponent_base_y}'

        if action == 8:
            if my_mana >= 10:
                opp_hero_in_hero_range = [
                    h for h in opp_heroes if in_range(h.x, h.y, hero.x, hero.y, 2200)]
                random_hero = random.choice(opp_hero_in_hero_range)
                if random_hero is not None:
                    cmds[index] = f'SPELL CONTROL {random_hero.id} {MAP_WIDTH//2} {MAP_HEIGHT//2}'

        if action == 9:
            cmds[index] = 'WAIT'

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
