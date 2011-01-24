from zope.interface import Interface
from zope import schema
from zope.component import getUtility
from z3c.appconfig.interfaces import IAppConfig
from zope.configuration import fields

class IAppConfigDirective(Interface):
    file = fields.Path(
            title=u"Path for configuration file to load.",
            required=True)

    clear = schema.Bool(
            title=u"Clear existing configuration before loading the config file.",
            default=False,
            required=False)


def LoadConfig(file, clear):
    config=getUtility(IAppConfig)
    config.loadConfig(file, clear)


def AppConfigDirective(_context, file, clear=False):
    _context.action(discriminator=("appconfig", file),
                    callable=LoadConfig,
                    args=(file, clear))

