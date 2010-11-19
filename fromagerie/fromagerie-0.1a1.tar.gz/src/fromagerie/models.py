# https://svn.python.org/packages/trunk/pypi/pkgbase_schema.sql
# http://docs.python.org/distutils/setupscript.html#additional-meta-data
#             ':action': action,
#             'metadata_version' : '1.0',
#             'name': meta.get_name(),
#             'version': meta.get_version(),
#             'summary': meta.get_description(),
#             'home_page': meta.get_url(),
#             'author': meta.get_contact(),
#             'author_email': meta.get_contact_email(),
#             'license': meta.get_licence(),
#             'description': meta.get_long_description(),
#             'keywords': meta.get_keywords(),
#             'platform': meta.get_platforms(),
#             'classifiers': meta.get_classifiers(), ==> List of Strings
#             'download_url': meta.get_download_url(),
#             # PEP 314 --> not required
#             'provides': meta.get_provides(),
#             'requires': meta.get_requires(),
#             'obsoletes': meta.get_obsoletes(),

# Required: name, version, url
# Requires either author & author_email, or maintainer & maintainer_email
# download_url & classifiers must not be present when python version is < 2.2.3 or < 2.3

# < 200 chars: name, version, author, maintainer, description

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from fromagerie.utils import safe_name

class Package(models.Model):
    """
    A module registered with the index.
    """
    name = models.CharField(_(u'name'), max_length=200, db_index=True, primary_key=True)
    normalized_name = models.SlugField(_(u'normalized name'), max_length=200)

    class Meta:
        verbose_name = _(u'package')
        verbose_name_plural = _(u'packages')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        if not self.normalized_name:
            self.normalized_name = safe_name(self.name).lower()
        super(Package, self).save(force_insert=force_insert, force_update=force_update)


class Release(models.Model):
    """
    A released version of a registered module.
    """
    package = models.ForeignKey(Package, verbose_name=_(u'package'), related_name='releases')
    version = models.CharField(_(u'version'), max_length=200)
    author = models.CharField(_(u'author'), max_length=200, blank=True)
    author_email = models.EmailField(_(u'author email'), max_length=254, blank=True)
    maintainer = models.CharField(_(u'maintainer'), max_length=200, blank=True)
    maintainer_email = models.EmailField(_(u'maintainer email'), max_length=254, blank=True)
    home_page = models.URLField(_(u'home page'), blank=True)
    license = models.TextField(_(u'license'), blank=True)
    summary = models.CharField(_(u'summary'), max_length=200, blank=True) # description
    description = models.TextField(_(u'description'), blank=True) # long_description
    description_html = models.TextField(_(u'description html'), editable=False)
    download_url = models.URLField(_(u'download URL'), blank=True)
    hidden = models.BooleanField(_(u'is hidden?'), default=False)
    added = models.DateTimeField(_(u'added'), default=datetime.datetime.now, editable=False)
    keywords = models.TextField(_(u'keywords'), blank=True)
    platform = models.TextField(_(u'platform'), blank=True)
    classifiers = models.ManyToManyField('Classifier', verbose_name=_(u'classifiers'), blank=True)

    class Meta:
        verbose_name = _(u'release')
        verbose_name_plural = _(u'releases')
        unique_together = ('package', 'version')

    def __unicode__(self):
        return u'%s-%s' % (self.package.name, self.version)


class ReleaseFile(models.Model):
    """
    Metadata about a release version file.
    """
    release = models.ForeignKey(Release, verbose_name=_(u'release'), related_name='files')
    content = models.FileField(_(u'distribution file'), upload_to='packages')
    filetype = models.CharField(_(u'distribution type'), max_length=200)
    md5_digest = models.CharField(_(u'MD5 digest'), max_length=32, blank=True)
    gpg_signature = models.TextField(_(u'GPG signature'), blank=True)
    pyversion = models.CharField(_(u'python version'), max_length=200, blank=True)
    upload_time = models.DateTimeField(_(u'upload time'), default=datetime.datetime.now, editable=False)
    comment = models.TextField(_(u'comment'), blank=True)

    class Meta:
        verbose_name = _(u'release file')
        verbose_name_plural = _(u'release files')

    def __unicode__(self):
        return u'%s-%s: %s %s' % (self.release.package.name, self.release.version, self.content.name, self.pyversion)

# Provides, Requires, Obsoletes? 

class Classifier(models.Model):
    """
    A hierarchical classification label.
    """
    name = models.CharField(_(u'name'), max_length=200, unique=True)
    parent = models.ForeignKey('self', verbose_name=_(u'parent'), related_name='children', null=True, blank=True)

    class Meta:
        verbose_name = _(u'classifier')
        verbose_name_plural = _(u'classifiers')

    def __unicode__(self):
        return self.name

class Role(models.Model):
    """
    A role a user plays for a package.
    """
    type = models.PositiveIntegerField(_(u'role type'))
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    package = models.ForeignKey(Package, verbose_name=_(u'package'))

    class Meta:
        verbose_name = _(u'role')
        verbose_name_plural = _(u'roles')

    def __unicode__(self):
        return u'%s - %s - %s' % (unicode(package), self.get_type_display(), unicode(user))
