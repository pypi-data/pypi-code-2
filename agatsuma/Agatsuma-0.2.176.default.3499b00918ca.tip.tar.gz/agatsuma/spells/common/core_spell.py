# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, IInternalSpell, ISetupSpell

from agatsuma.commons.types import Atom

class CoreSpell(AbstractSpell, IInternalSpell, ISetupSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Core Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_core, config)

    def pre_configure(self, core):
        core.register_option("!core.debug", bool, "Debug mode")

    def requirements(self):
        return {"autodoc" : ["Sphinx>=0.6.5"],
               }
