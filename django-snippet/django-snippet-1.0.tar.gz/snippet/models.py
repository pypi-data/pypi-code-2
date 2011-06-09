from django.db import models
from tinymce import models as tinymce_models

# Create your models here.
class Snippet(models.Model):
	name = models.CharField(max_length=255)
	content = tinymce_models.HTMLField(blank = True)
	
	def __unicode__(self):
		return self.name
		
