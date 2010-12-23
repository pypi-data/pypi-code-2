# me2.plugs.wave/clone.py
#
#

""" clone the wave after x blips. """

## me2 imports

from me2.lib.commands import cmnds
from me2.lib.callbacks import callbacks
from me2.lib.gae.wave.waves import Wave
from me2.lib.plugins import plugs

## basic imports

import logging

## callbacks

def clonepre(bot, event):
    if event.bottype == "wave":
        return True

def clonecallback(bot, event):
    wave = event.chan
    if wave.data.threshold != -1 and (wave.data.seenblips > wave.data.threshold):
        wave.data.threshold = -1
        newwave = wave.clone(bot, event, event.title)
        plugs.load('me2.plugs.common.hubbub')
        feeds = plugs['me2.plugs.common.hubbub'].watcher.clone(bot.name, bot.type, newwave.data.waveid, event.waveid)
        event.reply("this wave is continued to %s with the following feeds: %s" % (newwave.data.url, feeds))

#callbacks.add("BLIP_SUBMITTED", clonecallback, clonepre)
#callbacks.add('OUTPUT', clonecallback, clonepre)
