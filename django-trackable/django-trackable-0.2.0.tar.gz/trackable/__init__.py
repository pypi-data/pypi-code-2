# from trackable.models import TrackableData, TrackableTimeSeriesData, TrackableError
# from trackable.sites import TrackableRegistry, site


class TrackableError(Exception):
    pass

def autodiscover():
    """
    Auto-discover INSTALLED_APPS trackabledata.py modules and fail silently when
    not present. 

    """
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(site._registry)
            import_module('%s.trackabledata' % app)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            site._registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'trackabledata'):
                raise

