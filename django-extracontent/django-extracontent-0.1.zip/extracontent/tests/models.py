from extracontent.models import ExtraContent
from extracontent.forms import ExtraContentForm
from django.db import models

class ExtraData1(models.Model):
    description = models.TextField()

    
class ExtraData2(models.Model):
    dt = models.DateField()
    
    
class MainModel(ExtraContent):
    name = models.CharField(max_length = 60)
    
class MainModel2(ExtraContent):
    name = models.CharField(max_length = 60)
    
MainModel2.register_one2one()
    
    
class MainModelForm(ExtraContentForm):
    
    class Meta:
        model = MainModel
        
class MainModelForm2(ExtraContentForm):
    
    class Meta:
        model = MainModel2