# gozerbot/plugs/reload.py
#
#

""" reload plugin. """

## me2 imports

from me2.utils.exception import handle_exception, exceptionmsg
from me2.lib.commands import cmnds
from me2.lib.examples import examples
from me2.lib.boot import savecmndtable, savepluginlist, update_mod
from me2.lib.errors import NoSuchPlugin

## basic imports

import os
import logging

## reload command

def handle_reload(bot, ievent):
    """ reload list of plugins. """
    try: pluglist = ievent.args
    except IndexError:
        ievent.missing('<list plugins>')
        return
    reloaded = []
    errors = []
    from me2.lib.boot import plugin_packages
    for plug in pluglist:
        for package in plugin_packages:
            modname = "%s.%s" % (package, plug)
            try:
                if bot.plugs.reload(modname, force=True, showerror=False):
                    update_mod(modname)
                    reloaded.append(modname)
                    logging.warn("reload - %s reloaded" % modname) 
                    break
            except NoSuchPlugin: continue
            except Exception, ex:
                if 'No module named' in str(ex):
                    logging.debug('reload - %s - %s' % (modname, str(ex)))
                    continue
                errors.append(exceptionmsg())
    if reloaded: ievent.reply('reloaded: ', reloaded)
    if errors: ievent.reply('errors: ', errors)

cmnds.add('reload', handle_reload, 'OPER')
examples.add('reload', 'reload <plugin>', 'reload core')
