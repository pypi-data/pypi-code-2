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

from _base import __copyright__, __author__, __url__, __version__

### Imports ###

from d6 import *

from math import factorial
fac = factorial # yes, I’m lazy :)

from random import choice

import yaml


### Constants ###

#: Example sourcedata for creating a character.
_examplechar = """
desc:
   name: Tsiku
   quote: Me eat you hat.
   short: Strange traveller.
   description: A strange traveller with hazel-colored eyes
     and fur.
extras: {}
stats:
   attributes:
      creative: [3, 0] # the first value is always the cost
      stubborn: [3, 0] # cost, mod
   skills:
      surprise: [3, "", creative] # cost, base, atts
      startle: [3, surprise, creative]
   special: {}
   battle:
      wound threshold: stubborn
"""

#: An example profile for automated character improvement.
_exampleprofile = """
attributes:
   witty: 3
   pure: 1
skills:
   hide: 1
special:
   rich: 1
"""

### Functions ###

def _attvalue(cost):
    """get the base attribute value from the number of marks paid for it.

    >>> _attvalue(-13)
    5
    >>> _attvalue(-9)
    6
    >>> _attvalue(-1)
    11
    >>> _attvalue(0)
    12
    >>> _attvalue(1)
    13
    >>> _attvalue(3)
    15
    >>> _attvalue(4)
    15
    >>> _attvalue(5)
    16
    >>> _attvalue(9)
    18
    >>> _attvalue(11)
    18
    >>> _attvalue(12)
    19
    """
    step = 1
    value = 12
    for i in range(abs(cost)):
        value += 1/step * cost/abs(cost) # reduce if < 0
        if not (i+1)%3 and (i+1)/3 == step*(step+1)/2:
            step += 1
    if cost > 0:
        return int(value+0.000001) # avoid a 1/3+1/3+1/3 rounding error
    else:
        return int(value+0.999999) # avoid a 1/3+1/3+1/3 rounding error

def _attvalue2cost(value):
    """Get the cost from the attvalue."""
    # naive implementation: Just try it out.
    cost = 0
    while _attvalue(cost) != abs(value):
        cost += 1
    return int(cost * value/max(1, abs(value))) # for negative values


def _cost2valueweight(cost):
    """cost to bonusweight: The weight for a stat which has a value value and the given cost, for choosing a stat to improve.

    >>> _cost2attvalueweight(0)
    1
    >>> _cost2attvalueweight(-5)
    1
    >>> _cost2attvalueweight(1)
    1
    >>> _cost2attvalueweight(2)
    1
    >>> _cost2attvalueweight(3)
    1
    >>> _cost2attvalueweight(4)
    2
    >>> _cost2attvalueweight(5)
    1
    >>> _cost2attvalueweight(6)
    2
    >>> _cost2attvalueweight(9)
    1
    >>> _cost2attvalueweight(11)
    3
    >>> _cost2attvalueweight(12)
    1
    """
    return max(cost - _attvaluecost(_costattvalue(cost)) + 1, 1)


def _cost2bonus(cost):
    """Cost to Bonus: Get the bonus from the cost: the number of points you paid.

    >>> _cost2bonus(0)
    0
    >>> _cost2bonus(1)
    0
    >>> _cost2bonus(3)
    1
    >>> _cost2bonus(8)
    1
    >>> _cost2bonus(9)
    2
    >>> _cost2bonus(10)
    2
    >>> _cost2bonus(-1)
    0
    >>> _cost2bonus(-2)
    0
    >>> _cost2bonus(-3)
    -1
    """
    step = 1
    for i in range(abs(cost)):
        if not (i+1)%3 and (i+1)/3 == step*(step+1)/2:
            step += 1
    step -= 1
    return int(step * cost/max(1, abs(cost)))

def _bonus2cost(bonus):
    """Get the cost needed to generate the given bonus."""
    # naive implementation: Just try it out.
    cost = 0
    while _cost2bonus(cost) != abs(bonus):
        cost += 1
    return int(cost * bonus/max(1, abs(bonus))) # for negative boni

def _cost2bonusweight(cost):
    """cost to bonusweight: The weight for a stat which only gives bonus with the given cost, for choosing a stat to improve.

    >>> _cost2bonusweight(0)
    1
    >>> _cost2bonusweight(-5)
    1
    >>> _cost2bonusweight(3)
    1
    >>> _cost2bonusweight(4)
    2
    >>> _cost2bonusweight(5)
    3
    >>> _cost2bonusweight(6)
    4
    >>> _cost2bonusweight(9)
    1
    """
    return max(cost - _bonus2cost(_cost2bonus(cost)) + 1, 1)

def _cost2valueweight(cost):
    """The weight for a stat which has a value with the given cost, for choosing a stat to improve.

    """
    return max(cost - _bonus2cost(_cost2bonus(cost)) + 1, 1)


def _skillvalue(cost):
    """Calculate the base value of a skill from its cost.

    This uses 1/3rd mark precision, suitable for weak characters
    (points, SwaC module)."""
    if cost < 3:
        if cost < 1:
            if cost < 1/3: return 3
            if cost < 2/3: return 6
            if cost < 1: return 8
        if cost < 5/3: return 9
        if cost <7/3: return 10
        return 11
    return _attvalue(cost) - 3

def _skillvaluefrom(basevalue, cost, attboni):
    """Get the skill value from its base skill (for specializations),
    its cost and the attribute boni."""
    bonus = int( sum([bonus for bonus in attboni]) )
    if not basevalue:
        return _skillvalue(cost) + bonus
    return basevalue + (_attvalue(cost) - 12) + bonus


### Custom Exceptions ###

class InvalidStatsError(BaseException):
    """The character has an invalid attribute, skill or similar."""
    pass


### Classes ###

class Att(object):
    """An attribute of a char.

    It gets a name, a cost and a modifier (from base attributes,
    species or such) and calculates from those the attribute value.
    """
    def __init__(self, name, cost, modifier=0):
        self.name = name
        self.cost = cost
        self.modifier = modifier
    @property
    def value(self):
        """The modified value used for rolling dice."""
        return _attvalue(self.cost) + self.modifier
    @property
    def rawvalue(self):
        """The raw value calculated from the cost."""
        return _attvalue(self.cost)
    @property
    def bonus(self):
        """The Bonus this skill can grant in the right situations, and
        the plusses it has."""
        return _cost2bonus(self.cost)
    def __repr__(self):
        return "Attr('" + self.name + "', " + str(self.cost) + ", " + str(self.modifier) + ")"


class Skill(object):
    """A skill of a char.

    It gets a a name, a cost, a base skill (for specializations) and
    up to two base attributes calculates from those the effective
    skill value."""
    def __init__(self, name, cost, base=None, atts=[]):
        self.name = name
        self.cost = cost
        self.atts = atts
        if base is self:
            raise InvalidStatsError("A Skill must not use itself as base.")
        if base is not None and base.base is self:
            raise InvalidStatsError("The base of a skill must not use the skill as base.")
        self.base = base
    @property
    def value(self):
        """The modified value used for rolling dice."""
        if self.base:
            return _skillvaluefrom(self.base.value, self.cost, (att.bonus for att in self.atts))
        else:
            return _skillvaluefrom(0, self.cost, (att.bonus for att in self.atts))
    @property
    def rawvalue(self):
        """The raw value calculated from the cost."""
        return _skillvalue(self.cost)
    @property
    def bonus(self):
        """The Bonus this skill can grant in the right situations, and
        the plusses it has."""
        return _costbonus(self.cost)
    def __repr__(self):
        return "Skill('" + self.name + "', " + str(self.cost) + ", " + self.base.__repr__() + ", '" + str(self.atts) + "')"


class Special(object):
    """A special ability of a char.

    At first this will only get a cost.
    On the long term this will need parsing specific to the game world."""
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
    @property
    def bonus(self):
        """The strength of the special ability: its plusses."""
        return _costbonus(self.cost)
    def __repr__(self):
        return "Skill('" + self.name + "', " + str(self.cost) + "')"


class BaseChar(object):
    """A basic 1d6 character which only holds values which can be changed but cannot act itself."""
    def __init__(self, source=_examplechar, profile=_exampleprofile):
        # load base data
        self.data = yaml.load(source)
        self.profile = yaml.load(profile)
        # atts
        _atts = self.data["stats"]["attributes"]
        self.atts = {name: Att(name, _atts[name][0], _atts[name][1])
                           for name in _atts}
        # skills
        _skills = self.data["stats"]["skills"]
        self.skills = {name: Skill(name, _skills[name][0],
                                   Skill("", 0, None, []), # base has to be added in a second phase.
                                   [self.atts.get(att, Att(name, 0)) # default: 12
                                    for att in _skills[name][2:]])
                       for name in _skills}
        for skill in self.skills.values():
            _hasbase = _skills[skill.name][1]
            if _hasbase:
                skill.base = self.skills[_hasbase]

        # special
        _special = self.data["stats"]["special"]
        self.special = {name: Special(name, _special[name])
                        for name in _special}

        # battle values
        _battle = self.data["stats"]["battle"]
        self.wounds = _battle.get("wounds", [0, 0])
        self.damage = _battle.get("damage", 0)
        # descriptive values
        self.desc = self.data["desc"]
        # extra
        self.extras = self.data["extras"]

    @property
    def name(self):
        try:
            return self.desc["name"]
        except KeyError:
            return ""
    @name.setter
    def name(self, name):
        self.desc["name"] = name

    @property
    def woundthresholdatt(self):
        return self.data["stats"]["battle"].get("wound threshold", Att("", 0))
    @woundthresholdatt.setter
    def woundthresholdatt(self, name):
        self.data["stats"]["battle"]["wound threshold"] = name

    @property
    def woundthreshold(self):
        """The wound threshold of the character. If he/she/it gets
        this much or more damage, he/she/it gets a wound."""
        _battle = self.data["stats"]["battle"]
        return 4 + self.atts.get(
            _battle.get("wound threshold", None),
            Att("res", 0)).bonus

    @property
    def cost(self):
        """The amount of experience the character has."""
        return sum([stat.cost for stat in self.skills.values()] +
                   [stat.cost for stat in self.atts.values()] +
                   [stat.cost for stat in self.special.values()])

    def _updatedata(self):
        """Update the raw data of the character. Everything but the skill and attribute costs should be done automatically."""
        _skills = self.data["stats"]["skills"]
        for skill in self.skills:
            sk = self.skills[skill]
            _skills[skill] = [sk.cost, sk.base.name] + [att.name for att in sk.atts]

        _atts = self.data["stats"]["attributes"]
        for att in self.atts:
            a = self.atts[att]
            _atts[att] = [a.cost, a.modifier]

        _special = self.data["stats"]["special"]
        for spec in self.special:
            s = self.special[spec]
            _special[spec] = s.cost

        _battle = self.data["stats"]["battle"]
        if not self.wounds[0] == 0 or not self.wounds[1] == 0:
                _battle["wounds"] = self.wounds
        else:
            if "wounds" in _battle: del _battle["wounds"]
        if not self.damage == 0:
                _battle["damage"] = self.damage
        else:
            if "damage" in _battle: del _battle["damage"]



    def __repr__(self):
        self._updatedata()
        return "Char(source='''" + yaml.dump(self.data) + "''', profile='''" + yaml.dump(self.profile) + "''')"

    def __str__(self):
        self._updatedata()
        return yaml.dump(self.data)


    def _tuple2stat(self, tup):
        """turn a (kind, name) tuple into a stat. If necessary create the stat."""
        kind, name = tup
        if kind == "attribute": _kind = self.atts
        elif kind == "skill": _kind = self.skills
        elif kind == "special": _kind = self.special
        else: raise InvalidStatsError("Unknown type of stat", kind)
        if name in _kind:
            return _kind[name]
        else:
            if kind == "attribute":
                _kind[name] = Att(name, 0)
            elif kind == "skill":
                _kind[name] = Skill(name, 0, Skill("", 0, None, []))
            elif kind == "special":
                _kind[name] = Special(name, 0)
        return _kind[name]


    def improve(self, cost, stat=None):
        """Improve a character by giving it additional marks (the cost).

        @param stat: (kind, name); kind = skill or attribute or special. """
        if stat is not None:
            stat = self._tuple2stat(stat)
            stat.cost += cost
            return
        atts = self.atts.values()
        skills = self.skills.values()
        special = self.special.values()
        # TODO: This is damn slow. Make it faster.
        while cost:
            weighted = []
            # stats it already has
            for stat in atts:
                for i in range(_cost2valueweight(stat.cost)):
                    weighted.append(("attribute", stat.name))
            for stat in skills:
                if cost > 0 or stat.cost >= 1: # skills can’t go below 0
                    for i in range(_cost2valueweight(stat.cost)):
                        weighted.append(("skill", stat.name))
            for stat in special:
                for i in range(_cost2bonusweight(stat.cost)):
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
            if cost > 1:
                self.improve(1, choice(weighted))
                cost -= 1
            elif cost < 1:
                self.improve(-1, choice(weighted))
                cost += 1
            else:
                self.improve(cost, choice(weighted))
                cost = 0


class Char(BaseChar):
    """An 1d6 character with actions."""
    def __init__(self, source=_examplechar, profile=_exampleprofile):
        super().__init__(source, profile)

    def roll(self, kind, name):
        """Roll an open test on a stat.

        @param kind: the type of stat: attribute or skill.
        @param name: the name of the stat.

        >>> c = Char()
        >>> res = c.roll("attribute", "creative")
        >>> c.roll("special", "fuck")
        Traceback (most recent call last):
        ...
        InvalidStatsError: ('you can’t roll an open test on', 'special', 'fuck', 'because it has no value.')
        """
        try:
            value = self._tuple2stat((kind, name)).value
        except AttributeError:
            raise InvalidStatsError("you can’t roll an open test on", kind, name, "because it has no value.")
        return roll(value)




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
    b.improve(-500)
    b.improve(500)
    b.roll("attribute", "creative")
    b.roll("skill", "startle")
    b.skills["startle"].rawvalue
    #print(b)

if __name__ == "__main__":
    _test()
