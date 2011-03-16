from utils.base import Command

class Kick(Command):
    _plugin_name = 'kick'

    triggers = {
        'do_kick': ['kick', 'k'],
        'deop': ['deop'],
    }

    def do_kick(self, irc, user, channel, args):
        if len(args) >=  1:
            user = user.split('!')[0]

            if user == 'xintron':
                irc.kick(channel, args.pop(0), ''.join(args))

    def deop(self, irc, user, channel, args):
        if len(args) >= 1:
            irc.mode(channel, False, 'o', user = args[0])
