import Skype4Py

SKYPE_HOOK_OPTIONS = {
    'Transport': 'x11',
}

def get_skype(**kwargs):
    options = kwargs or {}
    return Skype4Py.Skype(**options)
