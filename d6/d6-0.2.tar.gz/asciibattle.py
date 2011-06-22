#!/usr/bin/env python3

"""A very simple battlefield script.

Fighters have one of three types: swordmaster (S), armored (A) or killer (K). They differ in their abilities.

"""

X, Y = 60, 30
rows = 30

from d6.char import Char
from random import choice, randint, shuffle
from termctl import *

#: Example sourcedata for creating a character.
_swordmaster = """
desc:
   name: Swordmaster
   description: Swift with the sword but little armor and weak weapon.
extras: {}
stats:
   attributes:
      swift: [3, 0] # the first value is always the cost
   skills:
      sword: [30, "", swift] # cost, base, atts
   special: {}
   battle:
      wound threshold: hardened
"""

_armored = """
desc:
   name: Armored
   description: In heavy armor to survive any strike
extras: {}
stats:
   attributes:
      hardened: [3, 0] # the first value is always the cost
   skills:
      sword: [7, "", swift] # cost, base, atts # 17
   special: {}
   battle:
      wound threshold: hardened
"""

_killer = """
desc:
   name: Killer
   description: With a deadly weapon to kill any foe.
extras: {}
stats:
   attributes:
      hardened: [3, 0] # the first value is always the cost
   skills:
      sword: [3, "", swift] # cost, base, atts
   special: {}
   battle:
      wound threshold: hardened
"""

#: The default profile for all fighters
_profile = """
attributes:
   swift: 1
   hardened: 1
skills:
   sword: 1
special: {}
"""

battlefield = {}
team0 = []
team1 = []

fighters = [(_swordmaster, "S", 4, 2), (_armored, "A", 4, 14), (_killer, "K", 16, 2)]
#fighters = [(_swordmaster, "S", 4, 2), (_killer, "K", 16, 2)]

for i in range(Y-20):
    for j in range(rows): # 3 rows
        # left side
        source, letter, weapon, armor = choice(fighters)
        c = Char(source)
        team0.append(c)
        c.pos = (j, i+10) # x, y
        c.let = lightblue(letter.lower())
        c.letter = blue(letter)
        c.weapon = weapon
        c.armor = armor
        c.team = 0
        c.enemy = None

        # right side
        source, letter, weapon, armor = choice(fighters)
        c = Char(source)
        team1.append(c)
        c.pos = (X-j-1, i+10) # x, y
        c.let = lightred(letter.lower())
        c.letter = red(letter)
        c.weapon = weapon
        c.armor = armor
        c.team = 1
        c.enemy = None

# setup
for i in team0 + team1:
    battlefield[i.pos] = i

fighters = team0 + team1
shuffle(fighters)

def distancesquared(me, other):
    return (me[0]-other[0])**2 + (me[1]-other[1])**2

def distance(me, other):
    x = other.pos[0] - me.pos[0]
    y = other.pos[1] - me.pos[1]
    return x, y

def stepforward(me, other):
    x, y = distance(me, other)
    if abs(x) > abs(y):
        if x > 0:
            return me.pos[0] + 1, me.pos[1]
        elif x < 0:
            return me.pos[0] - 1, me.pos[1]
        else: return me.pos
    else:
        if y > 0:
            return me.pos[0], me.pos[1] + 1
        elif y < 0:
            return me.pos[0], me.pos[1] - 1
        else: return me.pos

def stepsideward(me, other):
    x, y = distance(me, other)
    if not abs(x) > abs(y):
        if x > 0:
            return me.pos[0] + 1, me.pos[1]
        elif x < 0:
            return me.pos[0] - 1, me.pos[1]
        else: return me.pos
    else:
        if y > 0:
            return me.pos[0], me.pos[1] + 1
        elif y < 0:
            return me.pos[0], me.pos[1] - 1
        else: return me.pos

def oddstep(me):
    return choice(adjadent(me.pos))

def adjadent(pos):
    left = pos[0] - 1, pos[1]
    right = pos[0] + 1, pos[1]
    up = pos[0], pos[1] - 1
    down = pos[0], pos[1] + 1
    return left, right, up, down

def draw():
    text = ""
    for y in range(Y+1):
        line = ""
        for x in range(X):
            if (x, y) in battlefield:
                line += battlefield[(x,y)].letter
            else:
                line += " "
        text += line + "\n"
    text += int(X/2 - 7)*" " + str(meancost(team0)) + " " + str(len(team0)) + " " + str(len(team1)) + " " + str(meancost(team1))
    stdout.write(text + "\n")

def findenemy(me):
    dist = 10000000000

    if me.team == 0:
        t = team1
    else:
        t = team0
    l = len(t)
    a = randint(0, l)
    b = randint(0, l)
    m = max(a, b)
    n = min(a, b)
    for c in t[n:m]:
        d = distancesquared(me.pos, c.pos)
        if d < dist:
            me.enemy = c
            dist = d

def attack(me, enemy, mod=0):
    win, damage, wounds = me.attack(enemy, "sword", me.weapon, me.armor, "sword", enemy.weapon, enemy.armor, mod)
    if win and wounds == 2:
        del battlefield[enemy.pos] # dead
        fighters.remove(enemy)
        if enemy.team == 0:
            team0.remove(enemy)
        else: team1.remove(enemy)
        me.enemy = None
        me.improve(6)
    elif not win and wounds == 2:
        del battlefield[me.pos]
        fighters.remove(me)
        if me.team == 0:
            team0.remove(me)
        else: team1.remove(me)
        enemy.enemy = None
        enemy.improve(6)
    elif win and wounds:
        me.improve(3)
    elif not win and wounds:
        enemy.improve(3)
    elif win:
        me.improve(1)
    else:
        enemy.improve(1)



def battleround():
    """a single round of battle"""
    for me in fighters[:]:
        if me.wounds[1]:
            continue
        if me.enemy is None or not me.enemy.pos in battlefield:
            findenemy(me)
        if me.enemy is None:
            continue
        forwards = stepforward(me, me.enemy)
        sidewards = stepsideward(me, me.enemy)
        odd = oddstep(me)
        for step in (forwards, sidewards, odd):
            if step in battlefield:
                isenemy = battlefield[step].team != me.team
                if isenemy:
                    me.enemy = battlefield[step]
                    enemies = len([battlefield[pos] for pos in adjadent(me.pos) if battlefield.get(pos, None) is not None and battlefield[pos].team != me.team])
                    allies = len([battlefield[pos] for pos in adjadent(me.enemy.pos) if battlefield.get(pos, None) is not None and battlefield[pos].team == me.team])
                    mod = (allies - enemies) * 3
                    attack(me, me.enemy, mod)
                    break
            else: # move there
                del battlefield[me.pos]
                me.pos = step
                battlefield[me.pos] = me
                break
        if me.wounds[0]:
            me.letter = me.let

def meancost(team):
    return int(sum((c.cost for c in team))/max(1, len(team)))

counter = 10
for i in range(100000):
    battleround()
    draw()
    erase()
    for i in range(Y+2):
        priorline()
    if len(team0) == 0 or len(team1) == 0:
        counter -= 1
    if counter <= 0:
        break
