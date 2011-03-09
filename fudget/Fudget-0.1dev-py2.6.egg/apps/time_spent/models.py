from django.db import models
from django.contrib.auth.models import User

class Income(models.Model):
	"""Income"""
	label = models.CharField(max_length=200)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	creator = models.ForeignKey(User)
	session_hash = models.CharField(max_length=200)

	# month_dt = models.DateTime()
	# TODO: consider an income per month
	# TODO: consider different number of hours per day

	def per_day(self, num_workdays):
		return float(self.amount) / float(num_workdays)

	def per_hour(self, num_workdays):
		print self.per_day(num_workdays) / 8.0
		return self.per_day(num_workdays) / 8.0

	def __unicode__(self):
		return "%s %s" % (self.label, self.amount)

class Expense(models.Model):
	dt = models.DateTimeField()
	label = models.CharField(max_length=200)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	creator = models.ForeignKey(User)
	session_hash = models.CharField(max_length=200)

	def __unicode__(self):
		return "%s %s" % (self.label, self.amount)

# class DemoSession(models.Model):
# 	"""Holds demo session ids"""
# 	session_hash = models.CharField(max_length=200)
# 	expense = models.ManyToManyField(Expense)
# 	income = models.ManyToManyField(Income)
# 
# class DemoAccount(models.Model):
# 	"""docstring for DemoAccount"""
# 	create_dt = models.DateTime()
# 	update_dt = models.DateTime()
# 
# class DemoAccountMap():
# 	"""docstring for DemoAccountMap"""
# 	account = models.Integer
# 	content_type = models.Integer()
# 	object_id = models.Integer()

