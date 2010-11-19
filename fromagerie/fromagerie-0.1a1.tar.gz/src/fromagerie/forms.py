import zipfile
import re
import os
try:
    from hashlib import md5 as md5constructor
except ImportError:
    from md5 import new as md5constructor

from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from fromagerie.models import Package, Release, ReleaseFile, Classifier
from fromagerie.utils import safe_name

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        exclude = ('normalized_name',) # 'owner'

class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Makes ModelMultipleChoiceField work with a ``to_field_name``.
    """
    def clean(self, value):
        if self.required and not value:
            raise forms.ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise forms.ValidationError(self.error_messages['list'])
        key = self.to_field_name or 'pk'
        for v in value:
            try:
                self.queryset.filter(**{key: v})
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid_pk_value'] % v)
        qs = self.queryset.filter(**{'%s__in' % key: value})
        ids = set([force_unicode(getattr(o, key)) for o in qs])
        for val in value:
            if force_unicode(val) not in ids:
                raise forms.ValidationError(self.error_messages['invalid_choice'] % val)
        return qs


class ReleaseForm(forms.ModelForm):
    """
    Validates a release's metadata.
    """
    name = forms.CharField(label=_(u'name'), max_length=200, required=True)
    classifiers = ModelMultipleChoiceField(Classifier.objects.all(), label=_(u'classifiers'), to_field_name='name', required=False)

    class Meta:
        model = Release
        exclude = ('package', 'hidden',)

    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        # We need to use the name, not the id
        self.fields['classifiers'].to_field_name = 'name'
        self.fields['classifiers'].queryset = Classifier.objects.all()

# File validation stuff

safe_zipnames = re.compile(r'(purelib|platlib|headers|scripts|data).+', re.I)

def is_distutils_file(file, filetype):
    """
    Basic check to see if we have a distutils file.
    """
    if file.name.endswith('.exe'):
        if filetype != 'bdist_wininst':
            return False
        try:
            zip_file = zipfile.ZipFile(file)
            name_list = zip_file.namelist()
        except zipfile.error:
            return False
        for file_name in name_list:
            if not safe_zipnames.match(file_name):
                return False
    elif file.name.endswith('.zip') or file.name.endswith('.egg'):
        try:
            zip_file = zipfile.ZipFile(file)
            name_list = zip_file.namelist()
        except zipfile.error:
            return False
        for file_name in name_list:
            name_parts = os.path.split(file_name)
            if len(name_parts) == 2 and name_parts[1] == 'PKG-INFO':
                break
        else:
            return False
    return True


def get_md5_digest(f):
    hash = md5constructor()
    for chunk in f.chunks():
        hash.update(chunk)
    return hash.hexdigest()

ASCII_ARMOR = '-----BEGIN PGP SIGNATURE-----'
DIST_TYPES = 'sdist bdist bdist_dumb bdist_rpm bdist_wininst'.split()

UPLOAD_ERROR_MESSAGES = {
    'missing_version': _(u'Python version is required for binary distribution uploads'),
    'invalid_distutils_file': _(u'Invalid distribution file'),
    'invalid_content_type': _(u'Invalid distribution file'),
    'invalid_filename': _(u'The filename must start with "%s", case insensitive'),
    'invalid_signature': _(u'The GPG signature is invalid'),
    'invalid_md5_digest': _(u'The MD5 digest does not match the MD5 digest of the given file'),
}

class ReleaseUploadForm(forms.ModelForm):
    """
    Validates a distribution file and its metadata for a given release.
    """
    # validate file -> correct mimetype, valid filename (matches package), filename does not already exist
    # validate md5 -> if provided, make sure it matches file
    # validate gpg -> make sure it has ascii-armor; comes in from distutils as a file
    # pyversion -> if not sdist, make sure we have specified a pyversion

    _error_messages = UPLOAD_ERROR_MESSAGES

    filetype = forms.ChoiceField(label=_(u'distribution type'), choices=zip(DIST_TYPES, DIST_TYPES), initial='sdist')
    gpg_signature = forms.FileField(label=_(u'GPG signature'), required=False)
    md5_digest = forms.RegexField(r'[0-9a-f]{32}', label=_(u'MD5 digest'), required=False)

    class Meta:
        model = ReleaseFile
        exclude = ('release', 'gpg_signature')

    def __init__(self, data=None, files=None, release=None, **kwargs):
        super(ReleaseUploadForm, self).__init__(data, files, **kwargs)
        self.release = release

    def clean_content(self):
        content = self.cleaned_data['content']
        filename = content.name
        # Validate content type
        if content.content_type.startswith('image/'):
            raise forms.ValidationError(self._error_messages['invalid_content_type'])
        # Validate filename
        prefix = safe_name(self.release.package.name.lower())
        if not safe_name(filename.lower()).startswith(prefix):
            raise forms.ValidationError(self._error_messages['invalid_filename'] % prefix)
        # validate a file with this name does not exist?
        # to do this: generate filename, check with storage backend?
        return content

    def clean_gpg_signature(self):
        signature = self.cleaned_data['gpg_signature']
        if signature:
#         if not signature.name.endswith('.asc'):
#             raise forms.ValidationError(self.invalid_signature)
            signature.open()
            if not signature.read(32).startswith(ASCII_ARMOR):
                raise forms.ValidationError(self._error_messsages['invalid_signature'])
        return signature

    def clean(self):
        """
        Verify dependent field properties.
        """
        data = self.cleaned_data
        content = data.get('content')
        filetype = data.get('filetype')
        if content and filetype:
            content.open()
            # Make sure binary distributions have a python version associated with them
            if filetype != 'sdist' and not data.get('pyversion'):
                self._errors['pyversion'] = ErrorList([self._error_messages['missing_version']])
            else:
                # Make sure the file matches expectations for the dist type
                if not is_distutils_file(content, filetype):
                    self._errors['content'] = ErrorList([self._error_messages['invalid_distutils_file']])
            # Make sure the given hash matches the given file's hash
            md5_digest = data.get('md5_digest')
            if md5_digest:
                if md5_digest != get_md5_digest(content):
                    self._errors['md5_digest'] = ErrorList([self._error_messages['invalid_md5_digest']])
        return data

    def save(self, commit=True):
        data = self.cleaned_data
        instance = super(ReleaseUploadForm, self).save(commit=False)
        instance.release = self.release
        # Populate the hash if not given
        if not instance.md5_digest:
            instance.md5_digest = get_md5_digest(data['content'])
        # Dump the signature file's contents to the signature text field
        signature = data.get('gpg_signature')
        if signature:
            instance.gpg_signature = signature.read()
        else:
            instance.gpg_signature = u''
        if commit:
            instance.save()
        return instance

# In future: check file type extensions against dist type?
# DIST_TYPES = 'sdist bdist bdist_dumb bdist_rpm bdist_wininst'.split()
# SDIST_TYPES = 'zip tar.gz tar.bz2 tar.Z tar'.split() 
# FILE_TYPES = {
#     'sdist': SDIST_TYPES,
#     'bdist': SDIST_TYPES + 'rpm srpm exe'.split(),
#     'bdist_rpm': 'rpm srpm'.split(),
#     'bdist_dumb': SDIST_TYPES,
#     'bdist_wininst': 'exe'.split(),
# }
