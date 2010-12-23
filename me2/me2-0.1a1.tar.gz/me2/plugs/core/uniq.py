# me2/plugs/uniq.py
#
# used in a pipeline .. unique elements """
# Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

""" used in a pipeline .. unique elements """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## me2 imports

from me2.lib.examples import examples
from me2.lib.commands import cmnds
from me2.utils.generic import waitforqueue

## uniq command

def handle_uniq(bot, ievent):
    """ uniq the result list """
    if not ievent.inqueue:
        ievent.reply('use uniq in a pipeline')
        return
    result = waitforqueue(ievent.inqueue, 30)
    if not result:
        ievent.reply('no data')
        return
    result = list(result)
    if not result: ievent.reply('no result')
    else: ievent.reply(result)

cmnds.add('uniq', handle_uniq, ['USER', 'GUEST', 'CLOUD'])
examples.add('uniq', 'sort out multiple elements', 'list | grep uniqe')
