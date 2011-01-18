# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import zope.component
import gocept.lms.interfaces
import logging

INTERVAL = datetime.timedelta(seconds=15)

log = logging.getLogger(__name__)


def notify():
    reference_time = datetime.datetime.now(pytz.UTC) - INTERVAL

    # Notify each client about URL changes that happened since the last
    # notification.
    clients = zope.component.getUtility(gocept.lms.interfaces.IClientProvider)
    for client in clients.values():
        notifications = gocept.lms.interfaces.INotifications(client)
        if not notifications.enabled:
            continue
        if notifications.last > reference_time:
            # don't notify clients more frequently than every 5 minutes
            continue
        notifications.notify()
