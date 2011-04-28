# -*- coding: utf-8 -*-

import Skype4Py
import time
import plugpy
import traceback

config = dict()
_plugin_path = None
_debug = False

class SimpleSkypePlugin(object):
    pass

class SkypePlugin(object):
    pass

plugin_classes = [SimpleSkypePlugin, SkypePlugin]

class PluginListPlugin(SimpleSkypePlugin):
    
    alias = "#plugins"
    
    def on_message(self, detail=None, *args, **kwargs):
        msg = []
        for k, v in plugpy._cache.items():
            if isinstance(k, str):
                info = plugpy.get_plugin_list(k)
                msg.append("%s:%s" % (k,info))
        return "\n".join(msg)
    
class PluginReloadPlugin(SimpleSkypePlugin):
    
    alias = "#reload"
    
    def on_message(self, *args, **kwargs):
        res = plugpy.reload_plugins(config, plugin_path=_plugin_path,
                plugin_class=plugin_classes, debug=_debug)

        return "reload ok"

def call_plugin(msg, event):
    try:
        plugpy.dispatch("message", msg, event, target=SkypePlugin)
        if event == u"RECEIVED":
            body =  msg.Body.split()
            if len(body) > 1:
                target, args = body[0], body[1:]
            else:
                target, args = body[0], ""
            res = plugpy.dispatch("message", *args, target=target)
            if res: 
                for retmsg, clazz in res:
                    msg.Chat.SendMessage(retmsg)
    except:
        plugpy.log(traceback.format_exc())

def on_message_handler(msg, event):
    call_plugin(msg, event)

def _main_loop(skype):
    while True:
        time.sleep(1)

def start(plugin_path=None, debug=False, log_handler=None,
        main_loop=_main_loop):
    
    _plugin_path = plugin_path
    _debug = debug
    res = plugpy.load_plugins(config, plugin_path=_plugin_path,
            plugin_class=plugin_classes, debug=_debug)
    skype = Skype4Py.Skype()
    skype.OnMessageStatus = on_message_handler
    skype.Attach()
    main_loop(skype)




