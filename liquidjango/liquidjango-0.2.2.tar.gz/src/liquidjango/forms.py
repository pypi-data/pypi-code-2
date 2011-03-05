#!/bin/bash
from django import forms
from django.core.files.temp import NamedTemporaryFile
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.http import HttpRequest
from liquidjango.models import Genre, Album, Playlist, Artist, Song
from liquidjango.utils import *
from liquidjango.index import *
from django.forms.models import modelformset_factory, inlineformset_factory , \
formset_factory, BaseInlineFormSet, BaseModelFormSet, BaseFormSet

class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_newfile])
    accept = forms.BooleanField(required=True,
            label=_('I declare I own the copyright of this material and or it is licensed under a free license'),
            help_text=_('(required)'))


class SongForm(forms.ModelForm):
    class Meta:
        model = Song


class SongInlineEditForm(SongForm):
    class Meta:
        model = Song
        #exclude = ('file', 'tags','artist','genre','date', 'license', 'url','comments')
        fields = ('title','artist','tracknumber')


class SongEditForm(SongForm):
    class Meta:
        model = Song
        exclude = ('file', 'tags')


class AllSongsinAlbumForm(forms.ModelForm):
    class Meta:
        model = Song
        exclude = ('file', 'title', 'tracknumber', 'tags')


                # Url: 


class PlaylistForm(forms.ModelForm):
    
    class Meta():
        model = Playlist
        exclude = ('songs', 'tags')



class MakeLastForm(forms.Form):
    entry = forms.IntegerField()

class EntryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.title



class CommandtoRadioForm(forms.Form):
    command = forms.CharField(max_length=140)

# list of dynamic playlists on the liquidsoap stream client:
#todo: generate it automatically from the info received by the liquidsoap
LIQ_PLS = [('music','music'), 
           ('nerd.1','nerd'),
           ('jingles.1', 'jingles')
          ]

class ReloadForm(forms.Form):
    playlist = forms.ChoiceField(choices=LIQ_PLS)

class EntryForm(forms.ModelForm):
    song = forms.CharField()
    class Meta:
        model = Entry


class TextEntryForm(forms.Form):

    song = forms.CheckboxInput()
    
    #class Meta:
    #    model = Entry
    #    exclude = ('position','playlist')



class TagForm(forms.ModelForm):
    button_css_class = 'button'

    class Meta:
        model = Tag

class AddTagForm(forms.Form):
    ''' to add tags to artists or songs

    if we wanted to use the TagForm forms.ModelForm, we could 
    get a 'tag already existing' error if we want to add an existing tag to a
    song that doest have it
    '''
    button_css_class = 'button'
    tag = forms.CharField()

PLAY_CHOICES = [
    'songs',
    'artists',
    'tags'
]
'''
class PlaySearchForm:
    play = forms.MultipleSelectField(label=_('play'),
                    choices=PLAY_CHOICES,
                    selected='song',
                    widget=forms.CheckboxSelectMultiple())

'''


class ImportURLForm(forms.Form):
    url = forms.URLField(label=_('insert link to an ogg file'),initial='http://')

class ImportFromArchive(forms.Form):
    path = forms.CharField()


MODEL_MAP = {
        'song': Song,
        'artist': Artist,
        'tag': Tag,
        'genre': Genre
}

MODEL_CHOICES = [('', 'all')] + zip(MODEL_MAP.keys(), MODEL_MAP.keys())


class SearchForm(forms.Form):
    query = forms.CharField(required=True,label=_('search'))
    model = forms.ChoiceField(choices=MODEL_CHOICES, required=False,
                              label=_('what'))

class AddSearchtoPls(forms.Form):
    songlist = forms.MultipleChoiceField(choices=[])

