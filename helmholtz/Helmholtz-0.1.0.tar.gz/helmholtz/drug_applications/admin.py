#encoding:utf-8
from django.contrib import admin
from helmholtz.drug_applications.models import Perfusion, Injection

drug_applications_admin = admin.site

drug_applications_admin.register(Perfusion)
drug_applications_admin.register(Injection)
