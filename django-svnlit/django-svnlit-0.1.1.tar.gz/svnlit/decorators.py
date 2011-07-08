import datetime

from django.conf import settings

from svnlit import models


_last_sync_check = datetime.datetime.fromtimestamp(0)


def autosync_repositories(view_func):
    def new_view_func(request, *args, **kwargs):
        global _last_sync_check

        if settings.SVNLIT_AUTO_SYNC:
            sync_td = datetime.timedelta(0, settings.SVNLIT_SYNC_INTERVAL)
            if datetime.datetime.now() - _last_sync_check > sync_td:
                threshold = datetime.datetime.now() - sync_td
                outdated_repositories = models.Repository.objects.filter(
                    last_synced__lte=threshold)
                for repository in outdated_repositories:
                    repository.sync()
                _last_sync_check = datetime.datetime.now()
                
        return view_func(request, *args, **kwargs)

    new_view_func.__name__ = view_func.__name__
    new_view_func.__dict__ = view_func.__dict__
    new_view_func.__doc__ = view_func.__doc__
    new_view_func.__module__ = view_func.__module__

    return new_view_func
