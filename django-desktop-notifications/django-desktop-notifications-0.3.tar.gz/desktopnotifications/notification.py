# -*- coding: utf-8 -*-

UDPHOST = "localhost"
UDPPORT = 8011

import socket
import traceback

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import simplejson as json
from desktopnotifications.models import DesktopNotification

@receiver(post_save, sender=DesktopNotification, dispatch_uid="send_desktop_notification")
def send_desktop_notification(sender, instance, **kwargs):
    """ This callback is used as post_save signal handler
    for anything you wanna monitor to send notification to.
    
    For example, I'm using it on DesktopNotification post_save signal.
    """
    datadict = {"action": "notification"}
    datadict.update(instance.get_user_dict())
    data = json.dumps(datadict)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(data, (UDPHOST, UDPPORT))
    finally:
        s.close()
        del s