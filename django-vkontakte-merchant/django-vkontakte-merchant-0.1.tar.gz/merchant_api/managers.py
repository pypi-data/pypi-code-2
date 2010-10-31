#coding: utf-8
from django.db import models

class TestOrderManager(models.Manager):
    def get_query_set(self):
        return super(TestOrderManager, self).get_query_set().filter(is_test=True)

class RealOrderManager(models.Manager):
    def get_query_set(self):
        return super(RealOrderManager, self).get_query_set().filter(is_test=False)

