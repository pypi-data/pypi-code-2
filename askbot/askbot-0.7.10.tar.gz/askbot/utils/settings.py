from django.conf import settings
from askbot.utils.loading import load_module

def get_setting(setting_name):
    mod_path = getattr(settings, 'EXTRA_SETTINGS_MODULE', 'django.conf.settings')
    settings_module = load_module(mod_path)
    return getattr(settings_module, setting_name)
