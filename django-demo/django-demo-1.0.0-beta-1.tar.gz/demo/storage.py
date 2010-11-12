from demo import settings
from demo.models import SessionDatabase
from demo.shared import THREAD_LOCALS
from django.core.files.storage import Storage

class BaseDemoStorage(object):
    def _save(self, name, content):
        realname = settings.FILE_STORAGE._save(self, name, content)
        SessionDatabase.objects.attach_file(THREAD_LOCALS.database, realname, )
        return realname
    
    
DemoStorage = type('DemoStorage', (BaseDemoStorage, settings.FILE_STORAGE, Storage),{})