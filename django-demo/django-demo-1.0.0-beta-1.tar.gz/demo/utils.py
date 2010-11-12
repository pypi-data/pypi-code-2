from demo import settings
from django.utils.importlib import import_module
try:
    from celery.decorators import task
except ImportError: # pragma: no cover
    def task(*args, **kwargs):
        def notadecorator(func):
            return func
        return notadecorator
    

class LazyImporter(object):
    """
    Prevents circular import issues
    """
    def __init__(self):
        self.modules = {}
        
    def get(self, module):
        if not module in self.modules: # pragma: no cover
            self.modules[module] = import_module(module)
        else:
            pass
        return self.modules[module]
    
lazy_imports = LazyImporter()
        


def get_celery_countdown():
    """
    Utility function that returns the 'countdown' argument for celery.
    """
    td = settings.DATABASE_LIVETIME 
    return td.seconds + td.microseconds / 1E6 + td.days * 86400

def kill_with_celery(session_database_id):
    return celery_killer.apply_async(args=[session_database_id], countdown=get_celery_countdown())

@task
def celery_killer(session_database_id):
    models = lazy_imports.get('demo.models')
    models.SessionDatabase.objects.get(pk=session_database_id).kill()