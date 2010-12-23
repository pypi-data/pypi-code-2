# me2/plugs/plug.py
#
#

""" plugin management. """

## me2 imports

from me2.lib.commands import cmnds
from me2.lib.examples import examples
from me2.lib.boot import default_plugins, plugin_packages, remove_plugin, update_mod

## plug-enable command

def handle_plugenable(bot, event):
    if not event.rest: event.missing("<plugin>") ; return
    mod = bot.plugs.getmodule(event.rest)
    if not mod: event.reply("can't find module for %s" % event.rest) ; return
    event.reply("reloading and enabling %s" % mod)
    bot.enable(mod)
    bot.plugs.load(mod, force=True)
    #update_mod(mod)
    event.done()

cmnds.add("plug-enable", handle_plugenable, ["OPER", ])
examples.add("plug-enable", "enable a plugin", "plug-enable me2.plugs.common.rss")

## plug-disable command

def handle_plugdisable(bot, event):
    if not event.rest: event.missing("<plugin>") ; return
    mod = bot.plugs.getmodule(event.rest)
    if mod in default_plugins: event.reply("can't remove a default plugin") ; return
    if not mod: event.reply("can't find module for %s" % event.rest) ; return
    event.reply("unloading and disabling %s" % mod)
    bot.plugs.unload(mod)
    bot.disable(mod)
    #remove_plugin(mod)
    event.done()

cmnds.add("plug-disable", handle_plugdisable, ["OPER", ])
examples.add("plug-disable", "disable a plugin", "plug-disable me2.plugs.common.rss")
