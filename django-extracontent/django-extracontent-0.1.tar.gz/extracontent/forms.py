from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory


class ExtraContentForm(forms.ModelForm):
    '''This model form handles extra content from a content type field
    The model must be an instance of :class:`ExtraContentModel`.
    '''    
    def __init__(self, data=None, **kwargs):
        instance = kwargs.get('instance',None)
        self.original_initial = kwargs.get('initial',None)
        self.original_data = data
        self.initial_extra = None if not instance else instance.extra_content
        super(ExtraContentForm,self).__init__(data=data, **kwargs)
        
    def is_valid(self):
        vi = super(ExtraContentForm,self).is_valid()
        cf = self.content_form()
        if cf:
            vi = cf.is_valid() and vi
            if vi:
                self.cleaned_data.update(cf.cleaned_data)
            else:
                self.errors.update(cf.errors)
        return vi
    
    def content_form(self):
        cf = getattr(self,'_content_form',False)
        if cf is False:
            data     = self.original_data
            initial  = self.original_initial
            instance = self.instance
            # If it is abound form we check the data first,
            # otherwise the initial, last the instance
            if self.is_bound:
                ct  = self._raw_value('content_type')
            elif initial:
                ct  = initial.get('content_type',None)
            else:
                ct = None
            if not ct:
                ct  = instance.content_type
            else:
                try:
                    ct = ContentType.objects.get(id = ct)
                except:
                    ct = None
            if ct:
                model = ct.model_class()
                content_form  = modelform_factory(model)
                instance = self.initial_extra
                if instance and not isinstance(instance,model):
                    opts = content_form._meta
                    initial_extra = forms.model_to_dict(instance, opts.fields, opts.exclude)
                    #Remove the id
                    initial_extra.pop(model._meta.pk.attname,None)
                    if data is not None:
                        initial_extra.update(dict(data.items()))
                        data = initial_extra
                    else:
                        if initial:
                            initial_extra.update(initial)
                        initial = initial_extra
                    instance = None
                cf = content_form(data = data, instance = instance, initial = initial)
            else:
                cf = None
            setattr(self,'_content_form',cf)
        return cf
    
    def save(self, commit = True):
        obj = super(ExtraContentForm,self).save(commit = commit)
        if not commit:
            return obj
        cf = self.content_form()
        if cf:
            obj._denormalise(cf.instance)
            new_extra = cf.save()
        else:
            new_extra = None
        obj.set_content(new_extra,self.initial_extra)
        return super(ExtraContentForm,self).save(commit = commit)
    
