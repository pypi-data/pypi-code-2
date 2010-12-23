# me2/factory.py
#
#

""" Factory to produce instances of classes. """

## me2 imports

from me2.lib.errors import NoSuchBotType

## Factory base class

class Factory(object):
     pass

## BotFactory class

class BotFactory(Factory):

    def create(self, type, cfg):
        if type == 'xmpp' or type == 'jabber':
            try:
                from me2.lib.gae.xmpp.bot import XMPPBot
                bot = XMPPBot(cfg)
            except ImportError:   
                from me2.lib.socklib.xmpp.bot import SXMPPBot
                bot = SXMPPBot(cfg)
        elif type == 'sxmpp':
            from me2.lib.socklib.xmpp.bot import SXMPPBot
            bot = SXMPPBot(cfg)
        elif type == 'web':
            from me2.lib.gae.web.bot import WebBot
            bot = WebBot(cfg)
        elif type == 'wave': 
            from me2.lib.gae.wave.bot import WaveBot
            bot = WaveBot(cfg, domain=cfg.domain)
        elif type == 'irc':
            from me2.lib.socklib.irc.bot import IRCBot
            bot = IRCBot(cfg)
        elif type == 'console':
            from me2.lib.console.bot import ConsoleBot
            bot = ConsoleBot(cfg)
        elif type == 'base':
            from me2.lib.botbase import BotBase
            bot = BotBase(cfg)
        else: raise NoSuchBotType('%s bot .. unproper type %s' % (type, cfg.dump()))
        return bot
