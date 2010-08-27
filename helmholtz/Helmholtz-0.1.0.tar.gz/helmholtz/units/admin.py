#encoding:utf-8
from django.contrib import admin
from helmholtz.units.models import Meaning, Unit

units_admin = admin.site

units_admin.register(Meaning)
units_admin.register(Unit)

