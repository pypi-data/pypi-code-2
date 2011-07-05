from loggers import log
from settings_meta import SettingsMeta

class LightweightSettings(object):
    __metaclass__ = SettingsMeta
    settings = {}

    @staticmethod
    def load_cfg_data(config_data):
        LightweightSettings.settings =  LightweightSettings.provider.load(config_data)
        if LightweightSettings.core.debug:
            print "Early config initialization completed"
            print LightweightSettings.provider.dump(LightweightSettings.settings)
            log.initiate(LightweightSettings.logging.to_dict())

    @staticmethod
    def update_callback():
        pass

    def __init__(self):
        class NothingToInstantiate(Exception):
            pass
        raise NothingToInstantiate()
