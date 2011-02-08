from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty 

from OFS.SimpleItem import SimpleItem

from interfaces import IAlertsConfiguration

class AlertsConfiguration(SimpleItem):
    implements(IAlertsConfiguration)

    for attr in IAlertsConfiguration.names():
        exec("%s = FieldProperty(IAlertsConfiguration['%s'])" % (attr, attr))


def config_adapter(context):
    return getUtility(IAlertsConfiguration,
                      name="collective.alerts-settings",
                      context=context)


class AlertsConfigFetcher:

    for attr in IAlertsConfiguration.names():
        exec("def %s(self): return self.config.%s" % (attr, attr))

    def __init__(self, context, REQUEST):
        self.config = config_adapter(context)
        




