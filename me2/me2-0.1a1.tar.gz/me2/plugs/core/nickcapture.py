# me2/plugs/nickcapture.py
#
#

""" nick recapture callback. """

## me2 imports

from me2.lib.callbacks import callbacks

## callbacks

def ncaptest(bot, ievent):
    """ test if user is splitted. """
    if '*.' in ievent.txt or bot.server in ievent.txt:
        return 0
    if bot.nick.lower() == ievent.nick.lower():
        return 1
    return 0

def ncap(bot, ievent):
    """ recapture the nick. """
    bot.donick(bot.orignick)

callbacks.add('QUIT', ncap, ncaptest, threaded=True)
