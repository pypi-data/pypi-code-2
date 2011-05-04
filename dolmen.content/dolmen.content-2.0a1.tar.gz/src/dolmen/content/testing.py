# -*- coding: utf-8 -*-

from grokcore.component import zcml
from zope.configuration.config import ConfigurationMachine


def grok(*modules):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.meta', config)
    for module in modules:
        zcml.do_grok(module, config)
    config.execute_actions()
