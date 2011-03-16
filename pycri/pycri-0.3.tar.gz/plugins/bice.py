import re

from pycri.plugins import Plugin, command


class Bice(Plugin):
    def on_privmsg(self, irc, prefix, params):
        channel = params[0]
        msg = params[-1]

        if re.search('bice', msg):
            irc.msg(channel, 'bice bice bice')
        return
