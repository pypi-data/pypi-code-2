from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Feedback(models.Model):
    user = models.ForeignKey(User, null=True)
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('E-Mail'))
    body = models.TextField(_("Feedback"))
    sent_time = models.DateTimeField(auto_now_add=True)