#!/usr/bin/env python
# -*- coding: utf-8 -*-

# simple_mod: a simple base mod for the kvigall calendar program
# Copyright (C) 2010  Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Do What The Fuck You Want To Public
# License, version 2, as published by Sam Hocevar. This program comes
# without any warranty, to the extent permitted by applicable law. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

##[ Name        ]## simple_mod [kvigall mod]
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Website     ]## <http://metanohi.org/projects/kvigall/mods/>
##[ Version     ]## 0.1.0
##[ Description ]##
##~~~~~~~~~~~~~~~\\\\
# This is a very basic mod, keeping everything very simple and
# easy. This should make it easier for people new to kvigall mods to
# create new kvigall mods.
#
# This script depends on kvigall, a free calendar program. You can
# download kvigall at <http://metanohi.org/projects/kvigall/>.
##~~~~~~~~~~~~~~~////
##[ Start date  ]## 2010 August 27

import kvigall.genericconnector as generic
from kvigall.various import Event

class Connector(generic.Connector):
    name='simple_mod' # Not really necessary
    title='Simple Mod' # Not that useful

    def init(self): # Not a typo; generic.Connector.__init__ calls init
        pass        # Nothing to do in a simple script. You might as
                    # well just delete this function.

    def start(self):
        pass # This is where you would usually have code connecting
             # you to e.g. a website. This function is optional.

    def end(self):
        pass # Useful if you have to disconnect something properly,
             # but not at all necessary.
        
    def get_kvigall_events(self, date):
        # Within date there's date.year, date.month and date.day

        # Since this is a basic example on how to use it, we'll just
        # return the same events no matter what date is given.
        events = []

        event = Event()
        event.type = 'Personal note'
        event.subject = 'Filling the trash bin'
        event.interval = ((10, 30), (14, 40)) # from 10:30 to 14:40
        event.author = 'Myself'
        event.projects = ('Team Trash', 'The Lazy Group')
        event.text = '''\
This is an important event. It's sole purpose is to be purposeful,
although that target in itself may turn out to be problematic in its
own right.\
'''
        events.append(event)

        event = Event()
        event.type = 'Sleep'
        event.subject = 'Sleeping'
        # We don't give an interval here.
        event.author = 'This person'
        event.projects = ('Ze Zleepers',
                          'The Human Being Research Facility')
        event.text = '''\
It has been decided that this person is to sleep in the specified
interval. This decision is final.\
'''
        events.append(event)

        return events

if __name__ == '__main__':
    print '''\
This is a kvigall mod. You cannot run it directly. kvigall
is a free calendar program downloadable at
<http://metanohi.org/projects/kvigall>.

You should run this as `kvigall [options] simple_mod`.\
'''
