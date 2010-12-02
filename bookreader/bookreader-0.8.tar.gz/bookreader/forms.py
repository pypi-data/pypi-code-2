from django import forms
from django.utils.translation import ugettext as _

from bookreader.models import Repository, Collection, Book, Page, Annotation



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
    
    sequence = forms.IntegerField(widget=forms.HiddenInput,
                                  required=False)
    
    internal = forms.BooleanField(widget=forms.HiddenInput, required=False)
    
    class Meta:
        model = Page
        fields = ('title','jp2','thumbnail','sequence', 'internal',)

class PageURLForm(forms.ModelForm):
    jp2 = forms.URLField(label=_(u'JPEG2000 URL'),
                         help_text=_(u'The URL for the high resolution JPEG2000 image of this page'),
                         required=False)
    
    thumbnail = forms.URLField(label=_(u'Thumbnail URL'),
                               help_text=_(u'The URL for a low resolution JPEG image of the page'),
                               required=False)
    
    class Meta:
        model = Page
        fields = ('jp2','thumbnail',)

class PageConversionForm(forms.ModelForm):
    title = forms.CharField(label=_(u'Page Title'),
                              required=False)
    sequence = forms.IntegerField(initial=0,
                                  widget=forms.HiddenInput)
    internal = forms.BooleanField(initial=False,
                                  widget=forms.HiddenInput,
                                  required=False)
    
    class Meta:
        model = Page
        fields = ('title','sequence','internal')

class CanonicalSelectionForm(forms.ModelForm):
    canonical = forms.ModelChoiceField(queryset=Book.objects.filter(is_canonical=True),
                                       empty_label='(None)',
                                       required=False)
    
    class Meta:
        model = Book
        fields = ('canonical',)

class AnnotationForm(forms.ModelForm):
    offset = forms.CharField(label=_(u'Starting Page'),
                             required=True)
    length = forms.CharField(label=_(u'Number of Pages'),
                             required=False)
    text = forms.CharField(label=_(u'Annotation Text'),
                           required=True,
                           widget=forms.Textarea(attrs={'rows': 3}))
    
    
    class Meta:
        model = Annotation
        fields = ('offset','length','structural','text',)

__all__ = ('DSpaceCollectionForm','DSpaceBookForm',)
