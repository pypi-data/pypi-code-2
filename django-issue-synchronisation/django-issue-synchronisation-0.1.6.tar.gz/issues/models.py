# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _


class Type(models.Model):
    """Represents a type of issue tracker.

    The type is used to distinguish between different issue trackers.
    """

    class Meta:
        db_table = u'k_ticketsystem'
        ordering = ('id',)
        verbose_name = _(u'Type')
        verbose_name_plural = _(u'Types')

    id = models.AutoField(db_column='ts_id', primary_key=True,
                          verbose_name=_(u'Id'))
    cid = models.CharField(db_column='ts_cid', unique=True, max_length=100,
                           verbose_name=_(u'CID'))
    name = models.CharField(db_column='ts_name', max_length=60,
                            verbose_name=_(u'Name'))
    description = models.CharField(db_column='ts_bez', max_length=255,
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    def __unicode__(self):
        return self.name


class Tracker(models.Model):
    """Reflects an issue tracker."""

    class Meta:
        db_table = u'ticketsystem'
        ordering = ('id',)
        verbose_name = _(u'Issue tracker')
        verbose_name_plural = _(u'Issue tracker')

    id = models.AutoField(db_column='tsy_id', primary_key=True,
                          verbose_name=_(u'Id'))
    type = models.ForeignKey('Type', db_column='tsy_tsid',
                             verbose_name=_(u'Type'))
    name = models.CharField(db_column='tsy_name', max_length=60,
                            verbose_name=_(u'Name'))
    config = models.CharField(db_column='tsy_config', max_length=255,
                              verbose_name=_(u'Configuration string'))
    active = models.BooleanField(db_column='tsy_aktiv',
                                 verbose_name=_(u'Active?'))
    last_update = models.DateTimeField(db_column='tsy_letzteaktualisierung',
                                       verbose_name=_(u'Last update'))

    def __unicode__(self):
        return self.name


class Issue(models.Model):
    """Basic issue storage class used for all issue trackers."""

    class Meta:
        db_table = u'ticket'
        ordering = ('id',)
        verbose_name = _(u'Issue')
        verbose_name_plural = _(u'Issues')

    id = models.AutoField(db_column='ti_id', primary_key=True,
                          verbose_name=_(u'Id'))
    title = models.CharField(db_column='ti_titel', max_length=255,
                             verbose_name=_(u'Title'))
    description = models.CharField(db_column='ti_beschreibung',
                                   max_length=5000,
                                   verbose_name=_(u'Description'))
    # The internal issue number (depends on the issue tracker)
    no = models.IntegerField(db_column='ti_nummer', verbose_name=_(u'No.'))
    reporter = models.CharField(db_column='ti_reporter', max_length=250,
                                verbose_name=_(u'Reporter'))
    owner = models.CharField(max_length=250,
                             verbose_name=_(u'Owner'))
    active = models.BooleanField(db_column='ti_aktiv',
                                 verbose_name=_(u'Active?'))
    master = models.ForeignKey('Issue', db_column='ti_master',
                               blank=True, null=True)
    tracker = models.ForeignKey('Tracker', db_column='ti_tsyid',
                                verbose_name=_(u'Issue tracker'))
    # Local timestamps
    created = models.DateTimeField(db_column='ti_crdate',
                                   verbose_name=_(u'Creation date'))
    updated = models.DateTimeField(db_column='ti_upddate',
                                   verbose_name=_(u'Update date'))
    # Remote timestamps
    last_change = models.DateTimeField(db_column='ti_letzteaenderung',
                                       verbose_name=_(u'Last change'))

    def __unicode__(self):
        return self.get_title() or str(self.__class__)

    @classmethod
    def by_tracker_id(cls, tracker, issue_no):
        """Returns an issue by its tracker.

        :param tracker: A :class:`Tracker` instance or id
        :param issue_no: The issue number (from within the tracker)
        :returns: Instance of :class:`Issue`
        """
        query = Issue.objects.filter(tracker=tracker, no=issue_no)
        if query.count() == 0:
            return Issue()
        else:
            return query[0]

    def get_title(self):
        """Returns the title of an issue."""
        if self.no and self.title:
            master = u''
            if self.master:
                master = u' (#%s)' % self.master.no
            return u'#%d%s: %s' % (self.no, master, self.title)
        elif not self.no and self.title:
            return self.title
        else:
            return None

    def set_title(self, value):
        """Set the title and strip value if necessary.

        :param value: The title value
        """
        assert isinstance(value, basestring)
        self.title = value[:255]

    def set_description(self, value):
        """Set the description and strip value if necessary.

        :param value: The title value
        """
        assert isinstance(value, basestring)
        self.description = value[:5000]


class IssueUser(models.Model):
    """Which users are related to an issue?."""

    id = models.AutoField(db_column='tn_id', primary_key=True,
                          verbose_name=_(u'Id'))
    user = models.ForeignKey(User, db_column='tn_userid',
                             verbose_name=_(u'User'))
    issue = models.ForeignKey('Issue', db_column='tn_tiid',
                              verbose_name=_(u'Issue'))

    class Meta:
        db_table = u'ticketnutzer'
        ordering = ('id',)
        verbose_name = _(u'Issue user')
        verbose_name_plural = _(u'Issue users')


class UserMapping(models.Model):
    """Defines a mapping between a user's issue tracking name and the internal user."""

    id = models.AutoField(db_column='nm_id', primary_key=True,
                          verbose_name=_(u'Id'))
    user = models.ForeignKey(User, db_column='nm_userid',
                             verbose_name=_(u'User'))
    tracker = models.ForeignKey('Tracker', db_column='nm_tsyid',
                                verbose_name=_(u'Issue tracker'))
    login_name = models.CharField(db_column='nm_loginname', max_length=255,
                                  verbose_name=_(u'Login name'))

    class Meta:
        db_table = u'nutzermapping'
        ordering = ('id',)
        verbose_name = _(u'User mapping')
        verbose_name_plural = _(u'User mapping')
