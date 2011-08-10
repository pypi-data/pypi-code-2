# gozerplugs/trac.py
#
#

from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.aliases import aliasset
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.tests import tests

cfg = PersistConfig()
cfg.define('baseurl', 'http://dev.gozerbot.org')

def handle_tracwiki(bot, ievent):
    if not ievent.rest:
        ievent.missing("<item>")
        return
    ievent.reply('%s/wiki/%s' % (cfg.get('baseurl'), ievent.rest))

cmnds.add('trac-wiki', handle_tracwiki, 'USER')
examples.add('trac-wiki', 'give t.e.o wiki url', 'trac-wiki TracAdmin')
aliasset('wiki', 'trac-wiki')
tests.add('trac-wiki README')
