# me2/plugs/tail.py
#
#

""" tail bot results. """

## me2 imports

from me2.utils.generic import waitforqueue
from me2.lib.commands import cmnds
from me2.lib.examples import examples

## tail command

def handle_tail(bot, ievent):
    """ used in a pipeline .. show last <nr> elements. """
    if not ievent.inqueue:
        ievent.reply("use tail in a pipeline")
        return
    try: nr = int(ievent.args[0])
    except (ValueError, IndexError):
        ievent.reply('tail <nr>')
        return
    result = waitforqueue(ievent.inqueue, 5)
    if not result:
        ievent.reply('no data to tail')
        return
    ievent.reply('results: ', result[-nr:])
    
cmnds.add('tail', handle_tail, ['USER', 'GUEST'])
examples.add('tail', 'show last <nr> lines of pipeline output', 'list | tail 5')
