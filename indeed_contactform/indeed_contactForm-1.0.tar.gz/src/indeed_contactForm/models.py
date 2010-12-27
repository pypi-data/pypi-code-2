from django.db import models


class Message(models.Model):
	date = models.DateField()
	subject = models.CharField(max_length=100)
	mail = models.EmailField()
	message = models.TextField(max_length=300)
	new = models.BooleanField()

	def __unicode__(self):
		return str(self.date)
