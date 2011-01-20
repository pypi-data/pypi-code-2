""" Utilities fonction, today only used for generic notification interface
"""
import zicbee_lib as zl

def notify(title=None, description=None, icon=None, timeout=None):
    """ Ouputs some notification thru the desktop

    :param title: title of the notification
    :type title: unicode

    :param description: corpse of the notification test
    :type description: unicode

    :param icon: the icon you want to use
    :type icon: text corresponding to a `shortname` or URI

    :param timeout: the timeout delay, in miliseconds
    :type timeout: int
    """
    zl.debug.log.info("[%s] %s: %s"%(icon, title, description))

try:
    if not zl.config.config.notify:
        raise ValueError('notify disabled in user settings')
    from .notify import notify
except ValueError, e:
    zl.debug.log.warning("Not loading notification: %s", e.args[0])
except Exception, e:
    zl.debug.log.error("Can't load notify framework! %s"%e)
    zl.debug.DEBUG(False)

