from utils.base import Command

class Slap(Command):
    _plugin_name = 'Slap'

    triggers = {
        'do_slap': ['slap']
    }

    def do_slap(self, irc, user, channel, args):
        if len(args) >= 1:
            user = user.split('!')[0]

            irc.msg(channel, '{} wants me to slap {}.. Oh, what the hell!'.format(user, args[0]))
            irc.me(channel, 'slaps {} around a bit with a large trout'.format(args[0]))
