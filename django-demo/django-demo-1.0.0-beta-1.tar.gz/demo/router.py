from demo.settings import IGNORES
from demo.shared import THREAD_LOCALS


class DemoRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label in IGNORES:
            return 'default'
        if THREAD_LOCALS.database:
            return THREAD_LOCALS.database.get_name()
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label in IGNORES:
            return 'default'
        if THREAD_LOCALS.database:
            return THREAD_LOCALS.database.get_name()
        return None