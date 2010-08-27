#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.drug_applications.admin import drug_applications_admin

urlpatterns = patterns('',
    (r'^admin/', include(drug_applications_admin.urls)),
) 
