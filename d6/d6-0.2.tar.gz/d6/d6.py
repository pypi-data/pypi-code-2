#!/bin/env python3

"""Do tests/checks (skills, etc.) according to the ±W6 rules → Throw a die."""

try:
    from ._base import __copyright__, __author__, __url__, __version__
except ValueError: # called within the package
    from _base import __copyright__, __author__, __url__, __version__



#### IMPORTS ####

from random import randint as rnd

d6values = (-5, -3, -1, 2, 4, 6)


#### FUNCTIONS ####

def d6():
    """Throw the ±W6/±D6 die."""
    # roll
    tmp = rnd(0,5)
    # potentially reroll
    count = 1
    if tmp in [0,5]:
            while tmp == rnd(0,5):
                    count += 1
    # get the value
    return count * d6values[tmp]


def roll(value):
    """Get a result value."""
    return value + d6()


def check(value, MW):
    """Check if the throw reaches a target number (MW)."""
    return roll(value) >= MW

def checkopen(value, MW):
    """Check if and by how much we manage to beat the target number or
    lose to it.

    @return True/False, absolute difference"""
    res = roll(value) - MW
    return res >= 0, abs(res)

def checkopenraw(value, MW):
    """Check if and by how much we manage to beat the target number or
    lose to it along with the raw result.

    @return True/False, absolute difference, raw result of the roll"""
    res = roll(value)
    return res >= MW, abs(res-MW), res

def contest(value0, value1):
    """Pitch two values against each other.

    @return win0 (True/False), absolute difference (always positive)"""
    return roll(value0) - roll(value1) >= 0

def contestopen(value0, value1):
    """Pitch two values against each other.

    @return win0 (True/False), absolute difference (always positive)"""
    diff = roll(value0) - roll(value1)
    return diff >= 0, abs(diff)

def contestopenraw(value0, value1):
    """Pitch two values against each other and also return their
    individual results.

    @return: win0 (True/False), difference, res0, res1 (raw result of the rolls)"""
    res0 = roll(value0)
    res1 = roll(value1)
    return res0 >= res1, abs(res0 - res1), res0, res1


#### SELF CHECK ####

if __name__ == '__main__':
        store = []
        for i in range(100000):
                store.append(d6())
        print ('min max')
        print (min(store), max(store))
