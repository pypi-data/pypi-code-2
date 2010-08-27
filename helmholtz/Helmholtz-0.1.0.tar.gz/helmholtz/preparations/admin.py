#encoding:utf-8
from django.contrib import admin
from helmholtz.preparations.models import Animal, InVivo, InVitroCulture, InSilico, InVitroSlice, AreaCentralis, EyeCorrection

class PreparationAdmin(admin.ModelAdmin):
    list_display = ['id', 'animal', 'protocol']

preparations_admin = admin.site

preparations_admin.register(Animal)
preparations_admin.register(InVivo, PreparationAdmin)
preparations_admin.register(InVitroCulture, PreparationAdmin)
preparations_admin.register(InSilico, PreparationAdmin)
preparations_admin.register(InVitroSlice, PreparationAdmin)
preparations_admin.register(AreaCentralis)
preparations_admin.register(EyeCorrection)
