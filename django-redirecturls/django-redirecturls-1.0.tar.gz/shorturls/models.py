from django.db import models

class Shorturls(models.Model):
    shortname = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
