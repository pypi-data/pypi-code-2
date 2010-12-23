# me2/plugs/welcome.py
#
#

""" send welcome message. """

## me2 imports

from me2.lib.commands import cmnds
from me2.lib.examples import examples

## welcome command

def handle_welcome(bot, event):
    event.reply("Welcome to BOTME2 .. The JSON everywhere bot ;] for wave/web/xmpp/IRC/console - you can give this bot commands. try !help.")

cmnds.add('welcome', handle_welcome, ['USER', 'GUEST'])
examples.add('welcome', 'send welcome msg', 'welcome')
