# plugs/timer.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.plugins import plugins
from gozerbot.plughelp import plughelp
from gozerbot.tests import tests

import time, copy

plughelp.add('timer', 'do a timing of a command')

def handle_timer(bot, ievent):
    """ do a timing of a command """
    if not ievent.rest:
        ievent.reply('<cmnd>')
        return
    event = copy.deepcopy(ievent)
    event.txt = ievent.rest
    event.onlyqueues = True
    starttime = time.time()
    result = plugins.cmnd(bot, event, 60)
    stoptime = time.time()
    if not result:
        ievent.reply('no result for %s' % ievent.rest)
        return
    result.insert(0, "%s seconds ==>" % str(stoptime-starttime))
    ievent.reply('timer results: ', result)

cmnds.add('timer', handle_timer, ['USER', 'WEB'], allowqueue=False, \
threaded=True)
examples.add('timer', 'time a command', 'timer version')
tests.add('timer version')
