from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class ExtraContentBase(models.Model):
    '''Abstract Model class for models with a dynamic content_type.
    '''
    extra_content_one2one = False
    object_id      = models.PositiveIntegerField(default = 0, editable = False)
    extra_content  = generic.GenericForeignKey('content_type', 'object_id')
    
    def __init__(self, *args, **kwargs):
        super(ExtraContentBase,self).__init__(*args, **kwargs)
    
    class Meta:
        abstract = True
    
    @property
    def type(self):
        if self.content_type:
            return self.content_type.name
        else:
            return ''
        
    def _denormalise(self, obj = None):
        return False
        
    def save(self, **kwargs):
        self.delete_cache()
        super(ExtraContentBase,self).save(**kwargs)
        if self._denormalise():
            self.extra_content.save()
            
    def set_content(self, obj, old_obj = None):
        old_obj = old_obj or self.extra_content
        if obj is not old_obj:
            if obj:
                self.content_type = ContentType.objects.get_for_model(obj)
                self.object_id = obj.pk
            else:
                self.content_type = None
                self.object_id = 0
            if old_obj and getattr(self.__class__,'_one2one',False):
                old_obj.delete()
    
    def delete_cache(self):
        for field in self._meta.virtual_fields:
            try:
                delattr(self,field.cache_attr)
            except:
                pass
                
    @classmethod
    def delete_extra_content(cls, instance = None, **kwargs):
        if isinstance(instance,cls):
            obj = instance.extra_content
            if obj:
                obj.delete()
    
    @classmethod
    def register_one2one(cls):
        '''Use this class method to register a one-to-one relationship with extra content'''
        from django.db.models import signals
        setattr(cls,'_one2one',True)
        signals.pre_delete.connect(cls.delete_extra_content, sender = cls)
        
        
class ExtraContent(ExtraContentBase):
    '''Abstract Model class for models with a dynamic content_type.
    '''
    content_type   = models.ForeignKey(ContentType, blank=True, null=True)
    
    class Meta:
        abstract = True

