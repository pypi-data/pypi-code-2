"""
Models for representing subversion repositories.
"""

import datetime
import posixpath
import mimetypes

from django.db import models
from django.core import exceptions
from django.utils import functional, safestring
from django.utils.translation import ugettext_lazy as _

from svnlit import managers, choices


class Repository(models.Model):
    """
    Meta data for a subversion repository.
    """
    uuid = models.CharField(max_length=128, editable=False)
    label = models.CharField(
        help_text=_('Unique label for the repository for use in the URL'),
        max_length=128, db_index=True, unique=True)
    root = models.CharField(
        help_text=_('Example: svn://example.com or file:///svn/'),
        max_length=512)
    uri = models.CharField(
        help_text=_('Externally facing URI for the repository, if available'),
        max_length=512, blank=True)
    is_private = models.BooleanField(default=False)

    username = models.CharField(max_length=512, blank=True)
    password = models.CharField(max_length=512, blank=True)

    last_synced = models.DateTimeField(
        default=functional.curry(datetime.datetime.fromtimestamp, 0),
        editable=False)

    objects = managers.RepositoryManager()

    class Meta:
        verbose_name_plural = _('repositories')
        ordering = ('label',)

    def __unicode__(self):
        return u'%s %s' % (self.label, self.root)

    def _get_login(self, realm, username, may_save):
        if not (self.username and self.password):
            raise exceptions.ImproperlyConfigured(_(
                'repository requires authentication, '
                'but no username and password available'))
        return (True, self.username, self.password, True)

    def sync(self):
        """
        Update the repository's changesets, and obtain the UUID if
        it's not set.
        """
        Repository.objects.sync(self)

    def sync_uuid(self):
        """
        Sync the repository UUID.
        """
        Repository.objects.sync_uuid(self)

    def sync_changesets(self):
        """
        Get all changes made to the repository since the
        `last_updated` datetime.
        """
        Repository.objects.sync_changesets(self)
        
    def get_latest_revision(self):
        """
        Get the latest revision of the repository.
        """
        revision = 0
        if self.changesets.count():
            revision = self.changesets.all()[0].revision
        return revision

    def get_node(self, path, revision=None):
        """
        Get a `svnlit.models.Node` object at the given
        path. Optionally specify a revision.
        """
        return Node.objects.get_or_sync(self, path, revision)
        

class Changeset(models.Model):
    """
    The meta data about a revision in a subversion repository.
    """
    repository = models.ForeignKey(Repository, related_name='changesets')
    date = models.DateTimeField()
    revision = models.PositiveIntegerField(db_index=True)
    author = models.CharField(max_length=512)
    message = models.TextField()

    class Meta:
        unique_together = (('repository', 'revision'),)
        ordering = ('-revision',)

    def __unicode__(self):
        return u'r%s' % self.revision

    def get_absolute_url(self):
        return ('svnlit_changeset', (self.repository.label, self.revision))
    get_absolute_url = models.permalink(get_absolute_url)

    def get_previous(self):
        """Get the previous changeset in the repository."""
        try:
            return self.repository.changesets.get(revision=self.revision - 1)
        except Changeset.DoesNotExist:
            return None

    def get_next(self):
        """Get the next changeset in the repository."""
        try:
            return self.repository.changesets.get(revision=self.revision + 1)
        except Changeset.DoesNotExist:
            return None


class Change(models.Model):
    """
    A changed path in a changeset, including the action taken.
    """
    changeset = models.ForeignKey(Changeset, related_name='changes')
    path = models.CharField(max_length=2048, db_index=True)
    action = models.CharField(max_length=1)

    copied_from_path = models.CharField(max_length=2048, null=True)
    copied_from_revision = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = (('changeset', 'path'),)
        ordering = ('changeset', 'path')

    def __unicode__(self):
        return u'%s %s' % (self.action, self.path)

    def _get_base_change(self):
        if hasattr(self, '_base_change'):
            return self._base_change
        if self.copied_from_revision is not None:
            self._base_change = Change.objects.get(
                changeset__repository=self.changeset.repository,
                revision=self.copied_from_revision)
            return self._base_change

    def is_addition(self):
        return self.action == 'A'

    def is_modification(self):
        return self.action == 'M'

    def is_deletion(self):
        return self.action == 'D'


class Node(models.Model):
    """
    The meta data for a path at a revision in a repository.

    Nodes can be understood as 'views' of a particular path in a
    repository at a particular revision number (a revision that may or
    may not have made changes at that path/revision). A node's actual
    content is stored in a separate model object, since the content
    may remain unchanged across a number of revisions at a particular
    path. The `get_last_changeset` method can be used to obtain the
    changeset and revision in which the node's path was last changed.

    This model largely reflects the information available through the
    subversion api. The field `cached` indicates when the data was
    retrieved from the api, and `cached_indirectly` indicates whether
    or not the node was generated from an api call for the node or
    from a related node (parent or one of its possible
    children). Indirectly cached nodes (which are usually nodes
    created as placeholders for heirarchical connections instead of
    through a direct api call) require another api call to collect the
    remaining missing information. Nodes can be optionally be included
    in a regular cleanup.
    """
    repository = models.ForeignKey(Repository, related_name='nodes')
    parent = models.ForeignKey('Node', related_name='children', null=True)
    path = models.CharField(max_length=2048, db_index=True)
    node_type = models.CharField(max_length=1)
    size = models.PositiveIntegerField(default=0)
    last_changed = models.DateTimeField(null=True)

    revision = models.PositiveIntegerField()
    cached = models.DateTimeField(default=datetime.datetime.now)
    cached_indirectly = models.BooleanField(default=True)

    content = models.ForeignKey('Content', related_name='nodes', null=True)

    objects = managers.NodeManager()

    class Meta:
        unique_together = (('repository', 'path', 'revision'),)
        ordering = ('node_type', 'path')

    def __unicode__(self):
        return u'%s@%s' % (self.path, self.revision)

    def iter_path(self):
        """
        Returns a generator that 'walks` up the node hierarchy,
        yielding each parent path until the root node is reached ('/').
        """
        path = self.path
        yield path
        while path != posixpath.sep:
            path = posixpath.split(path)[0]
            yield path

    def iter_path_basename(self):
        """
        Returns a generator that 'walks' up the node hierarchy,
        yielding a tuple of the path, and the basename of the path for
        each parent node until the root node is reached ('/').
        """
        for path in self.iter_path():
            basename = posixpath.basename(path)
            if not basename:
                basename = self.repository.label
            yield (path, basename)

    def get_last_changeset(self):
        """Get the latest `Changeset` object that affected this node."""
        c = self.repository.changesets.filter(
            date__lte=self.last_changed)#.exclude(revision=self.revision)
        if c.count():
            return c[0]
        else:
            return self.repository.changesets.get(date=self.last_changed)

    def get_absolute_url(self):
        repository = self.repository
        if self.revision != repository.get_latest_revision():
            return (
                'svnlit_node_revision', (
                repository.label, self.revision, self.path))
        else:
            return ('svnlit_node', (repository.label, self.path))
    get_absolute_url = models.permalink(get_absolute_url)

    def get_basename(self):
        """
        The basename of the node, either a file name or a directory
        name.
        """
        basename = posixpath.basename(self.path)
        return basename

    def is_directory(self):
        """Whether the node is a directory."""
        return self.node_type == choices.NODE_TYPE_DIR

    def is_file(self):
        """Whether the node is a file."""
        return self.node_type == choices.NODE_TYPE_FILE

    def is_root(self):
        """Whether the node is the root node ('/')."""
        return self.is_directory() and self.path == posixpath.sep

    def has_properties(self):
        """Whether the node has subversion properties set."""
        if self.properties.count():
            return True
        return False


class Property(models.Model):
    """
    A property that has been set on a node.
    """
    node = models.ForeignKey(Node, related_name='properties')
    key = models.CharField(max_length=512, db_index=True)
    value = models.TextField()

    class Meta:
        unique_together = (('node', 'key'),)
        verbose_name_plural = 'properties'

    def __unicode__(self):
        return '%s: %s' % (self.key, self.value)


class Content(models.Model):
    """
    The contents of a node at a revision.

    The data is base64 encoded in the database to allow storage of
    binary data. The `set_data` and `get_data` methods should be used
    to manipulate a node's data. `cached` indicates when the contents
    were retrieved from the api. Content objects can optionally be
    part of a regular cleanup.
    """
    repository = models.ForeignKey(Repository, related_name='content')
    path = models.CharField(max_length=2048)
    last_changed = models.DateTimeField()
    cached = models.DateTimeField(default=datetime.datetime.now)
    size = models.PositiveIntegerField(default=0)
    data = models.TextField()

    class Meta:
        unique_together = (('repository', 'path', 'last_changed'),)

    def __unicode__(self):
        return '%s@%s' % (self.path, self.get_last_changeset())

    def set_data(self, data):
        self.size = len(data)
        self.data = data.encode('base64')

    def get_data(self):
        if hasattr(self, '_decoded_data'):
            return self._decoded_data
        self._decoded_data = self.data.decode('base64')
        return self._decoded_data

    def get_last_changeset(self):
        """Get the changeset in which this content was committed."""
        return self.repository.changesets.get(date=self.last_changed)

    def get_mimetype(self):
        """
        Get the mimetype of the content. This is determined by the
        extension of the basename of the path. Defaults to
        application/octet-stream if the mimetype cannot be determined.
        """
        mtype = mimetypes.guess_type(self.path)[0]
        if mtype is None:
            return 'application/octet-stream'
        return mtype

    def get_maintype(self):
        """
        Get the maintype of the mimetype, i.e. 'image' in 'image/png'.
        """
        return self.get_mimetype().split('/')[0]

    def get_subtype(self):
        """
        Get the subtype of the mimetype, i.e. 'png' in 'image/png'.
        """
        return self.get_mimetype().split('/')[-1]

    def get_absolute_url(self):
        return ('svnlit_content', (
                self.repository.label, self.pk, self.get_basename()))
    get_absolute_url = models.permalink(get_absolute_url)

    def is_binary(self):
        """
        Whether or not the content is binary. This is determined in
        part by the mimetype, but if the mimetype is not available,
        then if the data cannot be decoded into ascii it will be
        presumed a binary format.
        """
        mtype = mimetypes.guess_type(self.path)[0]
        if mtype is None:
            try:
                self.get_data().decode('ascii')
            except UnicodeDecodeError:
                return True
            return False
        if not mtype.startswith('text'):
            return True
        return False

    def get_basename(self):
        """Get the basename of the node's full path (the filename)."""
        basename = posixpath.basename(self.path)
        return basename

    def get_data_display(self):
        """
        Get the content for display in text. Binary formats are just
        shown as '(binary)'. Plain text formats get run through the
        appropriate pygments lexer if the package is available.
        """
        if self.is_binary():
            return _('<pre>(binary)</pre>')

        txt = self.get_data()

        try:
            from pygments import highlight, lexers
            from pygments.formatters import HtmlFormatter
        except ImportError:
            return safestring.mark_safe('<pre>%s</pre>' % txt)

        try:
            lexer = lexers.guess_lexer(txt)
        except lexers.ClassNotFound:
            try:
                lexer = lexers.get_lexer_for_filename(self.get_basename())
            except:
                return safestring.mark_safe('<pre>%s</pre>' % txt)

        return safestring.mark_safe(
            highlight(txt, lexer, HtmlFormatter(linenos=True)))
