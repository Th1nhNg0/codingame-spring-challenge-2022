import sys
from collections import namedtuple

# print("Debug messages...", file=sys.stderr, flush=True)


Entity = namedtuple('Entity', [
    'id', 'type', 'x', 'y', 'shieldLife', 'isControlled', 'health', 'vx', 'vy', 'nearBase', 'threatFor'
])


def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2

# base_x,base_y: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())

# game loop
while True:
    my_health, my_mana = [int(j) for j in input().split()]
    enemy_health, enemy_mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

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
            threat_for      # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        )

        if _type == TYPE_MONSTER:
            monsters.append(entity)
        elif _type == TYPE_MY_HERO:
            my_heroes.append(entity)
        elif _type == TYPE_OP_HERO:
            opp_heroes.append(entity)

    # The monsters that is targeting my base
    monster_target_my_base = None

    # this monster is really near the base, so we must kill it at all cost -.-
    dangerous_monster_max_distance = 5500
    dangerous_monster = None

    if monsters:
        monster_target_my_base = [
            m for m in monsters if (m.nearBase == 1 and m.threatFor == 1) or (m.nearBase == 0 and m.threatFor == 1)]
        if monster_target_my_base:
            monster_target_my_base.sort(
                key=lambda m: distance(m.x, m.y, base_x, base_y))
            if distance(monster_target_my_base[0].x, monster_target_my_base[0].y, base_x, base_y) < dangerous_monster_max_distance:
                dangerous_monster = monster_target_my_base[0]
    for i in range(heroes_per_player):
        if dangerous_monster:
            print(
                f'MOVE {dangerous_monster.x} {dangerous_monster.y}')
            continue
        if monster_target_my_base:
            monster = monster_target_my_base[i % len(monster_target_my_base)]
            print(
                f'MOVE {monster.x} {monster.y}')
        else:
            if distance(my_heroes[i].x, my_heroes[i].y, base_x, base_y) > 3000:
                print(f'MOVE {base_x} {base_y}')
            else:
                print('WAIT')
