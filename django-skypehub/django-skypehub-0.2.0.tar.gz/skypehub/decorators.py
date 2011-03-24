from django.conf import settings

from skypehub.utils import get_skype

def skype_required(view):
    def _inner(request, *args, **kwargs):
        hook_options = getattr(settings, 'SKYPE_HOOK_OPTIONS',  {})
        skype = get_skype(**hook_options)
        return view(request, skype, *args, **kwargs)
    return _inner
