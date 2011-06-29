from django.db import models


class Chunk(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    text = models.TextField(blank=True)

    def __unicode__(self):
        return self.name
