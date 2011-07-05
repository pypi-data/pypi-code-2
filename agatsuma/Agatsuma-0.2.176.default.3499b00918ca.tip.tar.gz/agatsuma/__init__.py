# -*- coding: utf-8 -*-

try:
    from infrastructure import log
    from infrastructure import Settings, LightweightSettings
    from enumerator import Enumerator
    from spellbook import Spellbook
    from spell_helpers import Spell, SpellByStr, Implementations

    __all__ = ["Spell",
               "SpellByStr",
               "Implementations",
               "Settings",
               "LightweightSettings",
               "log",
               "Enumerator",
               ]
except Exception, e:
    print("Can't import core functionality: '%s', bootstrap required?" % str(e))
