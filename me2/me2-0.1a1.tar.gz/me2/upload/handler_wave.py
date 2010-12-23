# handler_wave.py
#
#

""" this handler handles all the wave jsonrpc requests. """

## me2 imports

from me2.lib.version import getversion
from me2.lib.errors import NoSuchCommand
from me2.lib.boot import boot

## gaelib imports

from me2.lib.gae.wave.bot import WaveBot

## basic imports

import logging
import os

## defines

logging.info(getversion('GAE WAVE'))
boot()

# the bot

bot = WaveBot(domain="googlewave.com")

def main():
    bot.run()

if __name__ == "__main__":
    main()
