#!/usr/bin/env python3

"""A character for the free 1d6 system.

A basic character has

* descriptions (name, quote, short form, visuals, …), ✔

* stats (attributes, skills, professions and specials,
  definitions which stats belong to specific values, i.e. wound
  threshhold), ✔

* extras (equipment, money and stuff which gives boni to specific
  rolls) ✔ (no content yet, though: just put in Char.extras)

* possible actions (do a skill or attribute roll or contest, describe
  yourself ✔, set or increase the cost and have the value change with it ✔) and

* a profile with weighted stats for automated character development. ✔

* simple status, like “active” (can it still act).

Design:

* Every stat the char has is a class with attributes, so I can just
  pass a stat to a function which then takes from it the data it needs.

A char is loaded from a yaml-formatted definition file which gives it
its basic data.

The stored data is the minimum amount of data needed. For example an
attribute needs only its name and cost (in marks). These can be loaded
to export a more expressive character file intended to be read by
humans.

TODO: Add professions to the chars.

"""

try:
    from ._base import __copyright__, __author__, __url__, __version__
except ValueError: # char.py called directly
    from _base import __copyright__, __author__, __url__, __version__

### Imports ###

try:
    from .d6 import *
    from .charbase import BaseChar, _examplechar, _exampleprofile, _cost2bonusweight, _cost2valueweight, InvalidStatsError
except ValueError:
    from d6 import *
    from charbase import BaseChar, _examplechar, _exampleprofile, _cost2bonusweight, _cost2valueweight, InvalidStatsError

from random import choice

### Classes ###

class Char(BaseChar):
    """An 1d6 character with actions."""
    def __init__(self, source=_examplechar, profile=_exampleprofile):
        super().__init__(source, profile)

    def improve(self, cost, stat=None):
        """Improve a character by giving it additional marks (the cost).

        @param stat: (kind, name); kind = skill or attribute or special.

        @return: [((kind, name), old value, new value), …]
        """
        if stat is not None:
            _stat = self._tuple2stat(stat)
            relevant = self._relevantvalue(_stat)
            _stat.cost += cost
            return [stat, relevant, self._relevantvalue(_stat)]
        atts = self.atts.values()
        skills = self.skills.values()
        special = self.special.values()
        improved = {} #: the improved stats
        # TODO: This is damn slow. Make it faster.
        while cost:
            weighted = []
            # stats it already has
            for stat in atts:
                for i in range(int(_cost2valueweight(stat.cost)+0.000001)):
                    weighted.append(("attribute", stat.name))
            for stat in skills:
                if cost > 0 or stat.cost >= 1: # skills can’t go below 0
                    for i in range(int(_cost2valueweight(stat.cost)+0.000001)):
                        weighted.append(("skill", stat.name))
            for stat in special:
                for i in range(int(_cost2bonusweight(stat.cost)+0.000001)):
                    weighted.append(("special", stat.name))
            # and stats from the profile
            for kind in self.profile:
                for stat in self.profile[kind]:
                    for i in range(self.profile[kind][stat]):
                        if kind == "attributes":
                            weighted.append(("attribute", stat))
                        elif kind == "skills":
                            if cost > 0: # skills can’t go below 0
                                weighted.append(("skill", stat))
                        elif kind == "special":
                            weighted.append(("special", stat))
                        else: raise InvalidStatsError("Unknown type of stat", kind)

            if not weighted:
                raise InvalidStatsError("The character has no values to improve")
            stat = choice(weighted)
            # store the initial value to be able to give a list of improvements.
            if not stat in improved:
                s = self._tuple2stat(stat)
                improved[stat] = self._relevantvalue(s)
            if cost > 1:
                self.improve(1, stat)
                cost -= 1
            elif cost < -1:
                self.improve(-1, stat)
                cost += 1
            else:
                self.improve(cost, stat)
                cost = 0

        # return the list of improvements
        return [( stat, improved[stat], self._relevantvalue(
                                            self._tuple2stat(stat)) )
                for stat in improved
                if improved[stat] != self._relevantvalue(
                                          self._tuple2stat(stat))]


    def roll(self, kind, name):
        """Roll an open test on a stat.

        @param kind: the type of stat: attribute or skill.
        @param name: the name of the stat.

        >>> c = Char()
        >>> res = c.roll("attribute", "creative")
        >>> c.roll("special", "fuck")
        Traceback (most recent call last):
        ...
        charbase.InvalidStatsError: ('you can’t roll an open test on', 'special', 'fuck', 'because it has no value.')
        """
        try:
            value = self._tuple2stat((kind, name)).value
        except AttributeError:
            raise InvalidStatsError("you can’t roll an open test on", kind, name, "because it has no value.")
        return roll(value) - 3*self.wounds[0] - 6*self.wounds[1]

    def compete(self, other, mykind, myname, otherkind, othername, bonus=0):
        """Compete against another char.

        @param mykind: the type of stat: attribute or skill.
        @param myname: the name of the stat.

        @return win: True/False, absolute difference
        """
        diff = self.roll(mykind, myname) - other.roll(otherkind, othername) + bonus
        return diff >= 0, abs(diff)

    def attack(self, other, myskill, myweapon, myarmor, otherskill, otherweapon, otherarmor, bonus=0):
        """Attack another char. THIS FUNCTION IS LIKELY TO BE REFACTORED to use character attributes to deliver the weapon and armor.

        @return win?, damage, wound? # wound: 0 = no, 1 = normal, 2 = critical
        """
        win, diff = self.compete(other, "skill", myskill, "skill", otherskill, bonus=bonus)

        if win:
            weapon = myweapon
            armor = otherarmor
            woundthreshold = other.woundthreshold
            hurt = other
        else:
            weapon = otherweapon
            armor = myarmor
            woundthreshold = self.woundthreshold
            hurt = self

        damage = max(diff + weapon - armor, 0) # can’t be negative

        if damage >= 3 * woundthreshold:
            wound = 2 # critical
            hurt.wounds[1] += 1
        elif damage >= woundthreshold:
            wound = 1 # normal
            hurt.wounds[0] += 1
        else: wound = 0

        hurt.damage += damage

        return win, damage, wound


### Self-Test ###

def _test():
    from doctest import testmod
    testmod()
    c = Char()
    b = eval(c.__repr__())
    assert b.skills["startle"].cost == 3
    cost = b.cost
    b.improve(5)
    assert b.cost == cost + 5
    b.improve(-20)
    #print([(s.name, s.cost, s.rawvalue, s.value) for s in b.skills.values()])
    b.improve(500)
    b.roll("attribute", "creative")
    b.roll("skill", "startle")
    b.skills["startle"].rawvalue
    #print(b)
    c.improve(100, ("skill", "startle"))
    c.wounds
    c.damage
    b.attack(c, "startle", 2, 1, "startle", 10, 7)
    c.wounds
    c.damage

if __name__ == "__main__":
    _test()
