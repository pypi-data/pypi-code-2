import logging

from config import AlertsConfiguration
from interfaces import IAlertsConfiguration

log = logging.getLogger("collective.alerts.setuphandlers.py")

def isNotAlertsProfile(self):
    return self.readDataFile("collective.alerts_marker.txt") is None

def registerUtilities(self):
    if isNotAlertsProfile(self):
        return 

    log.info('registerUtilities')
    sm = self.getSite().getSiteManager()
    if not sm.queryUtility(IAlertsConfiguration, 
                           name="collective.alerts-settings",
                           ):

        sm.registerUtility(AlertsConfiguration(),
                           IAlertsConfiguration,
                           "collective.alerts-settings",
                           )


