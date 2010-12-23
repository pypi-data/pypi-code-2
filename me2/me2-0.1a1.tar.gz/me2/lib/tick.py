# me2/tick.py
#
#

""" provide system wide clock tick. """

## me2 imports

from me2.lib.threadloop import TimedLoop
from me2.lib.eventbase import EventBase
from me2.lib.callbacks import callbacks

## TickLoop class

class TickLoop(TimedLoop):

    event = EventBase()
    event.type = event.cbtype = 'TICK'

    def start(self, bot=None):
        """ start the loop. """
        self.bot = bot
        TimedLoop.start(self)

    def handle(self):
        """ send TICK events to callback. """
        callbacks.check(self.bot, self.event)

## global tick loop

tickloop = TickLoop('tickloop', 60)
