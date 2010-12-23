# me2/plugs/gae.py
#
#

""" Google Application Engine related commands. """

## me2 imports

from me2.lib.commands import cmnds
from me2.lib.examples import examples

## commands

def handle_gaeflushcache(bot, ievent):
    """ flush the cache .. flush all with no arguments otherwise delete specific. """
    from google.appengine.api.memcache import flush_all, delete

    if not ievent.rest:
        flush_all()
    else:
        delete(ievent.rest)

    ievent.done()

cmnds.add('gae-flushcache', handle_gaeflushcache, 'OPER')
examples.add('gae-flushcache', 'flush the bots cache', 'gae-flushcache')

def handle_gaeadminstats(bot, ievent):
    """ show bot stats. """
    from google.appengine.api.memcache import get_stats
    ievent.reply("cache: %s" % str(get_stats()))

cmnds.add('gae-stats', handle_gaeadminstats, 'OPER')
examples.add('gae-stats', 'show bots stats', 'gae-stats')
