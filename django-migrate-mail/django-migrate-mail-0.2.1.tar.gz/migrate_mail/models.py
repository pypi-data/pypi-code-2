
from django.db import models
import datetime

class Migration(models.Model):
    domain = models.CharField(max_length=100, verbose_name=u'Google Apps Domain')
    admin_username = models.CharField(max_length=100, verbose_name=u'Domain admin username')
    admin_password = models.CharField(max_length=100, verbose_name=u'Domain admin password')
    from_email = models.EmailField(verbose_name=u'Source email address')
    from_password = models.CharField(max_length=100, verbose_name=u'Source email password')
    to_username = models.CharField(max_length=100, verbose_name=u'Destination Apps username')
    since = models.DateField(default=datetime.date(1990, 1, 1), verbose_name=u'Import emails since date')
    
    auth_token = models.TextField()
    labels_processed = models.BooleanField(default=False)
    current_since = models.DateField(default=datetime.date(1990, 1, 1))
    current_label = models.CharField(max_length=100, null=True, blank=True)
    messages_cnt = models.IntegerField(default=0)
    last_uid = models.IntegerField(default=0)

class Label(models.Model):
    migration = models.ForeignKey('Migration', related_name='labels')
    uid = models.IntegerField(db_index=True)
    label = models.CharField(max_length=100)
