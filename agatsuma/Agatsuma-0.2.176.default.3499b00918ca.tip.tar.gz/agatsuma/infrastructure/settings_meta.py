import threading

from agatsuma.infrastructure.access_proxy import SettingsGroupProxy
from agatsuma.infrastructure.yaml_settings_provider import YamlSettingsProvider as SettingsProvider
from agatsuma.infrastructure.loggers import log

class SettingsMeta(type):
    def __setattr__(stype, name, value):
       if name in type.__getattribute__(stype, "settings"):
           raise Exception("It's not allowed to overwrite settings group")
       else:
           type.__setattr__(stype, name, value)

    def __getattribute__(stype, name):
        settings = type.__getattribute__(stype, "settings")
        if name in settings:
            return SettingsGroupProxy(
                settings[name],
                name, # group
                stype.readonly_settings.get(name, []),
                stype.types.get(name, {}),
                stype.comments.get(name, {}),
                stype.update_callback
                )
        else:
            return type.__getattribute__(stype, name)

    def reset_fields(stype):
        stype.settings = {}
        stype.provider = SettingsProvider()
        stype.readonly_settings = {}
        stype.types = {}
        stype.comments = {}
        stype.config_lock = threading.Lock()

    def __log(stype, message):
        if hasattr(log, "settings"):
            log.settings.info(message)
        else:
            print message

    def load_config(stype, config, *args, **kwargs):
        stype.__log("Loading config '%s' in %s" % (config, stype.__name__))
        conf = open(config, 'r')
        conf_content = conf.read()
        conf.close()
        stype.reset_fields()
        stype.load_cfg_data(conf_content, *args, **kwargs)
        stype.__log("Config '%s' loaded by %s" % (config, stype.__name__))

