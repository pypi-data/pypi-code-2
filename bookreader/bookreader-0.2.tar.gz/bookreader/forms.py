from django import forms
from django.utils.translation import ugettext as _

from bookreader.models import Repository, Collection, Book, Page



class CollectionForm(forms.ModelForm):
    
    class Meta:
        model = Collection
        fields = ['repository','handle']
        

class DSpaceHandleForm(forms.Form):
    repository = forms.URLField(verify_exists=True, required=True, 
                                label=_(u'Repository URL'),
                                help_text=_(u'The OAI-PMH URL base for the repository.'))
    
    handle = forms.CharField(required=True,
                             label=_(u'Handle'),
                             help_text=_(u'The DSpace handle.'))

class DSpaceCollectionForm(DSpaceHandleForm):
    handle = forms.CharField(required=True,
                             label=_(u'Collection Handle'),
                             help_text=_(u'The DSpace handle for the collection.'))

class DSpaceBookForm(DSpaceHandleForm):
    handle = forms.CharField(required=True,
                             label=_(u'Book Handle'),
                             help_text=_(u'The DSpace handle for a book item.'))

__all__ = ('DSpaceCollectionForm','DSpaceBookForm',)
