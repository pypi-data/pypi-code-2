# -*- coding: utf-8 -*-
from utils import base

class Greet(base.Command):
    _plugin_name = 'Greeter'
    
    triggers = {
        'greet': ['hello'],
    }

    def greet(self, irc, user, channel, args):
        user = user.split('!')[0]

        irc.msg(channel, 'Well hello there {}. How are you today Sir?'.format(user))

    def on_user_joined(self, irc, user, channel):
        irc.msg(channel, 'Välkommen kära {}'.format(user.split('!')[0]))
