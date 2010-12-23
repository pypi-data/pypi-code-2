# me2/plugs/xmpp.py
#
#

""" xmpp related commands. """

## me2 imports

from me2.lib.commands import cmnds
from me2.lib.examples import examples
from me2.lib.fleet import getfleet

## xmpp-invite command

def handle_xmppinvite(bot, event):
    """ invite (subscribe to) a different user. """
    if not event.rest:
        event.missing("<list of jids>")
        return
    bot = getfleet().getfirstjabber()
    if bot:
        for jid in event.args: bot.invite(jid)
        event.done()
    else: event.reply("can't find jabber bot in fleet")

cmnds.add("xmpp-invite", handle_xmppinvite, 'OPER')
examples.add("xmpp-invite", "invite a user.", "xmpp-invite jsoncloud@appspot.com")
