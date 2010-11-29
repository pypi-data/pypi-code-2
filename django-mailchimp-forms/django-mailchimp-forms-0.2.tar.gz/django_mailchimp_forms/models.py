from django.contrib.auth.models import User
from django.db import models

class MailingList(models.Model):
    user = models.OneToOneField(User, blank=False, null=False)
    confirmed = models.BooleanField(default=False)
