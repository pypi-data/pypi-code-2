#encoding:utf-8
from django.contrib import admin
from helmholtz.annotation.models import Descriptor, TextAnnotation, DocumentAnnotation, IntegerObjectIsAnnotated, CharObjectIsAnnotated

annotation_admin = admin.site

annotation_admin.register(Descriptor)
annotation_admin.register(TextAnnotation)
annotation_admin.register(DocumentAnnotation)
annotation_admin.register(IntegerObjectIsAnnotated)
annotation_admin.register(CharObjectIsAnnotated)
