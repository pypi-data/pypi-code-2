from django import forms
from django.utils.translation import ugettext_lazy as _

from svnlit import models, exceptions


class RepositoryDiffForm(forms.Form):
    from_path = forms.CharField(
        max_length=1024, widget=forms.TextInput(attrs={'size': '40'}))
    from_revision = forms.CharField(
        widget=forms.TextInput(attrs={'size': '3'}))
    to_path = forms.CharField(
        max_length=1024, widget=forms.TextInput(attrs={'size': '40'}))
    to_revision = forms.CharField(
        widget=forms.TextInput(attrs={'size': '3'}))

    def __init__(self, *args, **kwargs):
        self.repository = kwargs.pop('repository')
        super(RepositoryDiffForm, self).__init__(*args, **kwargs)

    def clean(self):
        repository = self.repository
        from_path = self.cleaned_data.get('from_path', '')
        from_revision = self.cleaned_data.get('from_revision', '')
        to_path = self.cleaned_data.get('to_path', '')
        to_revision = self.cleaned_data.get('to_revision', '')

        if not (from_path and from_revision and to_path and to_revision):
            raise forms.ValidationError(
                _(('Please specify both path and '
                   'revision combinations to compare.')))

        if not from_revision.isdigit() or not to_revision.isdigit():
            raise forms.ValidationError(_('Revision should be a number.'))
        from_revision, to_revision = int(from_revision), int(to_revision)

        try:
            from_node = repository.get_node(from_path, from_revision)
        except exceptions.InvalidNode:
            raise forms.ValidationError(
                _('Non-existant node at the path/revision comparing from.'))
        try:
            to_node = repository.get_node(to_path, to_revision)
        except exceptions.InvalidNode:
            raise forms.ValidationError(
                _('Non-existant node at the path/revision comparing to.'))

        return {'from_node': from_node, 'to_node': to_node}
