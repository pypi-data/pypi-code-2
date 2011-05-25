from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

DESKTOP_NOTIFICATION_TAGS = getattr(settings, "DESKTOP_NOTIFICATION_TAGS", ())

class DesktopNotification(models.Model):
    class Meta:
        verbose_name = u"Desktop Notification"
        ordering = [ "-date_creation", ]
    
    def __unicode__(self):
        return u"For %s: %s" % (self.user, self.title,)
    
    user = models.ForeignKey(User, verbose_name=u"User")
    title = models.CharField(u"Title", max_length=128, blank=True)
    # HTML content
    content = models.TextField(u"Content", blank=False)
    autoclose = models.BooleanField(u"Automatic close", 
        default=True)
    autoclose_delay = models.IntegerField(u"Auto close delay", 
        default=-1, # -1 => Let the client choose
        help_text=u"Close delay in seconds. (Only if autoclose is True)")
    date_creation = models.DateTimeField(u"Date of creation", 
        auto_now_add=True, auto_now=True)
    
    tag = models.CharField(u"Tag", blank=False, max_length=128, choices = DESKTOP_NOTIFICATION_TAGS)
    
    def get_autoclose_delay(self):
        """ Returns the autoclose delay if set and autoclose is possible """
        if not self.autoclose:
            return 0
        return self.autoclose_delay
    
    def get_content(self):
        """ Maybe overridden """
        return self.content
    
    def get_user_dict(self):
        """ Returns the dict to nodejs => Relayed to end user """
        return {"notification_id": self.id,
                "username": self.user.username,
                "tag": self.tag,
                "autoclose_delay": self.get_autoclose_delay()
        }