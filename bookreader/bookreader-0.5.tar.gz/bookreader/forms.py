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

class PageForm(forms.ModelForm):
    
    title = forms.CharField(label=_(u'Page Title'),
                            help_text=_(u'Optional page title'),
                            required=False)
    
    jp2 = forms.URLField(label=_(u'JPEG2000 URL'),
                         help_text=_(u'The URL for the high resolution JPEG2000 image of this page'),
                         required=False)
    
    thumbnail = forms.URLField(label=_(u'Thumbnail URL'),
                               help_text=_(u'The URL for a low resolution JPEG image of the page'),
                               required=False)
    
    
    
    class Meta:
        model = Page
        fields = ('title','jp2','thumbnail',)


__all__ = ('DSpaceCollectionForm','DSpaceBookForm',)
