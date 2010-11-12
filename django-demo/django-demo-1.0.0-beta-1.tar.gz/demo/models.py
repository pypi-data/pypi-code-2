from datetime import datetime
from demo import settings
from demo.base import create_database, drop_database, install_database
from demo.exceptions import DatabaseLimit, DatabaseExpired
from demo.utils import kill_with_celery
from django.core.files.storage import default_storage
from django.db import models

def get_death():
    return datetime.now() + settings.DATABASE_LIVETIME


class SessionDatabaseManager(models.Manager):
    def get_database(self, request):
        session_id = request.session.session_key
        if not session_id: # pragma: no cover
            return None
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return self.new(session_id)
        session.database.install()
        return session.database
        
    def new(self, session_id):
        total = self.count()
        if settings.MAX_DATABASES and total >= settings.MAX_DATABASES:
            raise DatabaseLimit
        database = self.create(death=get_death())
        Session.objects.create(id=session_id, database=database)
        database.create()
        if settings.CELERY: # pragma: no cover
            kill_with_celery(database.pk)
        return database
    
    def kill(self):
        qs = self.filter(death__lt=datetime.now())
        for obj in qs:
            obj.kill(False)
        SessionFile.objects.delete(database__in=qs)
        Session.objects.filter(database__in=qs).delete()
        qs.delete()
        
    def reattach(self, old, new):
        old_session = Session.objects.get(id=old)
        Session.objects.create(id=new, database=old_session.database)
        old_session.delete()
        
    def get_next_death(self):
        if self.all().exists():
            return self.order_by('-death')[0]
        return datetime.now()
    
    def share(self, request):
        session_id = request.session.session_key
        if not session_id: # pragma: no cover
            return None
        source_id = request.GET[settings.SHARE_PARAMETER]
        try:
            source = Session.objects.get(id=source_id)
        except Session.DoesNotExist:
            raise DatabaseExpired
        Session.objects.create(id=session_id, database=source.database)
        return source.database.get_name()
    
    def get_death(self, request):
        session_id = request.session.session_key
        if not session_id: # pragma: no cover
            return None
        try:
            return self.get(sessions__id=session_id).death
        except self.model.DoesNotExist:
            return None
        
    def attach_file(self, database, filename):
        if not database: # pragma: no cover
            return
        SessionFile.objects.create(database=database, filename=filename)


class SessionDatabase(models.Model):
    death = models.DateTimeField()
    
    objects = SessionDatabaseManager()
    
    class Meta:
        ordering = ['-death']
    
    def __unicode__(self):
        return self.get_name()
    
    def get_name(self):
        return settings.DB_NAME_TEMPLATE % {'num': self.pk}
    
    def kill(self, delete=True):
        drop_database(self.get_name())
        if delete:
            SessionFile.objects.delete(database=self)
            self.sessions.all().delete()
            self.delete()
            
    def install(self):
        return install_database(self.get_name())
    
    def create(self):
        return create_database(self.get_name())
        
        
class Session(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    database = models.ForeignKey(SessionDatabase, related_name='sessions')
    
    def __unicode__(self): # pragma: no cover
        return '%s using %s' % (self.id, self.database.get_name())
    
    
class SessionFileManager(models.Manager):
    def delete(self, **kwargs):
        qs = self.filter(**kwargs)
        filenames = qs.values_list('filename', flat=True)
        for filename in filenames:
            if default_storage.exists(filename):
                default_storage.delete(filename)
            else: # pragma: no cover
                pass
        qs.delete()
    

class SessionFile(models.Model):
    database = models.ForeignKey(SessionDatabase, related_name='files')
    filename = models.CharField(max_length=512)
    
    objects = SessionFileManager()
    
    def __unicode__(self): # pragma: no cover
        return '%s on %s' % (self.filename, self.database)
    
    def delete(self, *args, **kwargs): # pragma: no cover
        if default_storage.exists(self.filename):
            default_storage.delete(self.filename)
        super(SessionFile, self).delete(*args, **kwargs)