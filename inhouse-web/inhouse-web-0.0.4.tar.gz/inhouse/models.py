# -*- coding: utf-8 -*-

import calendar
import cgi
import datetime
from decimal import Decimal
import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

#import filter
import managers
from issues.models import Issue, Tracker


# Roles
ROLE_ADMINISTRATOR = 1
ROLE_PROJECT_MANAGER = 2
ROLE_EMPLOYEE_INTERNAL = 3
ROLE_EMPLOYEE_EXTERNAL = 4
ROLE_HOLIDAY_MANAGER = 5

# Project status
PROJECT_STATUS_OPEN = 1
PROJECT_STATUS_DELETED = 2
PROJECT_STATUS_IDLE = 3
PROJECT_STATUS_CLOSED = 4

PROJECT_ACTIVE_STATUS = (
    PROJECT_STATUS_OPEN,
)

PROJECT_INACTIVE_STATUS = (
    PROJECT_STATUS_DELETED,
    PROJECT_STATUS_IDLE,
    PROJECT_STATUS_CLOSED,
)

# Step status
STEP_STATUS_OPEN = 1
STEP_STATUS_CLOSED = 2

PROJECT_STEP_INACTIVE_STATUS = (STEP_STATUS_CLOSED,)
PROJECT_STEP_ACTIVE_STATUS = (STEP_STATUS_OPEN,)

# Address groups
ADDRESS_GROUP_UNKOWN = 1
ADDRESS_GROUP_EMPLOYEE = 2
ADDRESS_GROUP_CUSTOMER = 3
ADDRESS_GROUP_APPLICANT = 4
ADDRESS_GROUP_SERVICE_PROVIDER = 5

# Countries
COUNTRY_UNKNOWN = 1

# Languages
LANGUAGE_UNKOWN = 1

# Priorities
PRIORITY_CHOICES = (
    (1, _(u'Low')),
    (2, _(u'Normal')),
    (3, _(u'High'))
)

TIMER_STATUS_ACTIVE = 1
TIMER_STATUS_STOPPED = 2

TIMER_CHOICES = (
    (TIMER_STATUS_ACTIVE, _(u'Running')),
    (TIMER_STATUS_STOPPED, _(u'Stopped')),
)

HISTORY_ACTION_DELETE = 'D'
HISTORY_ACTION_ADD = 'A'
HISTORY_ACTION_UPDATE = 'U'

HISTORY_ACTIONS = {HISTORY_ACTION_DELETE: _(u'deleted'),
                   HISTORY_ACTION_ADD: _(u'added'),
                   HISTORY_ACTION_UPDATE: _(u'updated')}

DEFAULT_COEFFICIENT_SATURDAY = Decimal("1.25")
DEFAULT_COEFFICIENT_SUNDAY = Decimal("1.5")
DEFAULT_COEFFICIENT_PROJECT_STEP = Decimal("1.0")


class Model(models.Model):
    """Abstract model class"""

    class Meta:
        abstract = True

    @classmethod
    def get_by_id(cls, id):
        """Returns a query object by it's primary key.

        :param id: Id of the query object
        :returns: Instance of cls or None
        """
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None
        query = cls.objects.filter(id=id)
        if query.count() == 0:
            raise cls.DoesNotExist
        elif query.count() == 1:
            return query[0]
        return query

    def save(self, *args, **kwds):
        """Derived save method to automatically save timestamp values."""
        now = datetime.datetime.now()
        user = kwds.pop('user')
        if not self.id:
            self.created = now
            self.created_by = user
        self.updated = now
        self.updated_by = user
        super(Model, self).save(*args, **kwds)


class Account(User):
    """Extension to Django`s :class:`User` object"""

    current_user_account = None
    starred_bookings = []
    undo_bookings = []

    class Meta:
        proxy = True

    @classmethod
    def get_account_for_user(cls, user):
        """Return a :class:`Account` instance by request.user

        :param user: A :class:`User` instance
        :returns: :class:`Account`
        """
        #if user.email:
            #query = Account.objects.filter(email=user.email)
            #account = tuple(query)[0] or None
        #else:
        query = Account.objects.filter(username=user.username)
        account = tuple(query)[0] or None
        if account is not None:
            return account

    @classmethod
    def get_short_name(cls, user):
        """Returns the shortened version of a profile name.

        :param cls: :class:`Account`
        :param user: A :class:`User` instance

        :returns: A string containing the short version of a name
        """
        if user.first_name and user.last_name:
            return '%.2s%.3s' % (user.first_name.title(),
                                 user.last_name.title())
        else:
            return None

    @property
    def nickname(self):
        """Return ether the first/lastname or the username.

        :returns: Username as string or first and last name.
        """
        if self.first_name and self.last_name:
            return u'%s %s' % (self.first_name, self.last_name)
        else:
            return self.username

    def create_profile(self):
        """Creates an empty user profile for an account."""
        user_profile = UserProfile()
        user_profile.user = self
        address = Address()
        address_group = AddressGroup.get_by_id(id=ADDRESS_GROUP_EMPLOYEE)
        address.group = address_group
        address.country = Country.get_by_id(id=COUNTRY_UNKNOWN)
        address.save(user=self)
        user_profile.address = address
        communication = Communication()
        communication.save(user=self)
        user_profile.communication = communication
        user_profile.save(user=self)

    # TODO: overload method to create profile automatically?
    # def get_profile

    def get_day(self, date):
        """Returns a :class:`Date` object or creates one.

        :param date: datetime.date instance

        :returns: :class:`Day` instance
        """
        try:
            day = Day.objects.get(date=date, user=self)
        except Day.DoesNotExist:
            day = Day.new(date, self)
            day.save(user=self)
        return day

    def get_bookable_customers(self):
        # TODO: Optimieren
        ids = []
        query = Customer.objects.all()
        for customer in query:
            if not customer.has_bookable_projects(user=self):
                continue
            if not self.works_for_customer(customer):
                continue
            ids.append(customer.id)
        query = Customer.objects.filter(id__in=ids)
        return query

    def get_starred_bookings(self):
        """Return all bookings, that are starred by the user.

        :returns: A :class:`Booking` query.
        """
        query = Booking.objects.select_related().filter(
            id__in=self.starred_bookings)
        return query

    def get_timers(self):
        query = Timer.objects.filter(created_by=self)
        query = query.order_by('created')
        return query

    def is_project_manager(self):
        pass

    def works_for_customer(self, customer):
        query = ProjectUser.objects.filter(user=self)
        query = query.filter(project__customer=customer)
        return query.count() > 0


class Address(Model):

    id = models.AutoField(db_column='adr_id', primary_key=True,
                          verbose_name=_(u'Id'))
    group = models.ForeignKey('AddressGroup', db_column='adr_adgid',
                              verbose_name=_(u'Address group'))
    name1 = models.CharField(max_length=200, db_column='adr_name1',
                             verbose_name=_(u'Name'))
    name2 = models.CharField(max_length=200, db_column='adr_name2',
                             blank=True, null=True,
                             verbose_name=_(u'Name'))
    name3 = models.CharField(max_length=200, db_column='adr_name3',
                             blank=True, null=True,
                             verbose_name=_(u'Name'))
    name4 = models.CharField(max_length=200, db_column='adr_name4',
                             blank=True, null=True,
                             verbose_name=_(u'Name'))
    street = models.CharField(db_column='adr_strasse', max_length=30,
                              blank=True, null=True,
                              verbose_name=_(u'Street'))
    zip_code = models.CharField(db_column='adr_plz', max_length=30,
                                blank=True, null=True,
                                verbose_name=_(u'ZIP code'))
    city = models.CharField(db_column='adr_ort', max_length=30,
                            blank=True, null=True,
                            verbose_name=_(u'City'))
    country = models.ForeignKey('Country', db_column='adr_laid',
                                verbose_name=_(u'Country'))
    post_office_box = models.CharField(db_column='adr_pf', max_length=100,
                                       blank=True, null=True,
                                       verbose_name=_(u'Post office box'))
    box_zip_code = models.IntegerField(db_column='kn_pfplz',
                                       blank=True, null=True,
                                       verbose_name=_(u'Box office code'))
    created_by = models.ForeignKey(User, db_column='adr_crid',
                                   null=True, related_name='address_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='adr_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='adr_updid',
                                   null=True, related_name='address_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='adr_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'adresse'
        verbose_name = _(u'Address')
        verbose_name_plural = _(u'Addresses')

    def __unicode__(self):
        return self.name1

    def get_addressstring(self, sep='<br />', *args, **kwds):
        """Returns an address as one single string.

        :param sep: Seperator string after earch address element.
        :returns: String with address information.
        """
        data = self.get_addresstuple(*args, **kwds)
        if '<' in sep:  # Separator is HTML/XML
            frmt = cgi.escape
        else:
            frmt = lambda x: x
        return sep.join(frmt(part) for part in data if part is not None)

    def get_addresstuple(self, names_only=False):
        """Return an address as a tuple.

        :param names_only: Return only the name part of the address

        :returns: Tuple with address elements
        """
        t = []
        if self.name1:
            t.append(self.name1)
        if self.name2:
            t.append(self.name2)
        if self.name3:
            t.append(self.name3)
        if self.name4:
            t.append(self.name4)
        if not names_only:
            if self.street:
                t.append(self.street)
            if self.city and not self.zip_code:
                t.append(self.city)
            elif self.city and self.zip_code:
                t.append('%s %s' % (self.zip_code, self.city))
            if self.country:
                t.append(str(self.country))
        return tuple(t)

    def get_join_name(self, join_char=''):
        """Return only the name fields joined together.

        :param join_char: The character used to join the name fields.
        :returns: String with address name fields.
        """
        parts = [self.name1, self.name2,
                 self.name3, self.name4]
        return join_char.join(cgi.escape(part) for part in parts
                              if part is not None)

    get_join_name_html = lambda me: me.get_join_name('<br />')


class AddressGroup(Model):

    id = models.AutoField(db_column='adg_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='adg_kbez', max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='adg_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    class Meta:
        db_table = u'k_adgrp'
        ordering = ('name',)
        verbose_name = _(u'Address group')
        verbose_name_plural = _(u'Address groups')

    def __unicode__(self):
        return self.name


class BillingType(Model):

    id = models.AutoField(db_column='aba_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='aba_kbez', max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='aba_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    class Meta:
        db_table = u'k_abrechnungsart'
        ordering = ('name',)
        verbose_name = _(u'Billing type')
        verbose_name_plural = _(u'Billing types')

    def __unicode__(self):
        return self.name


class Book(Model):

    id = models.AutoField(db_column='bu_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(max_length=100, db_column='bu_kbez',
                            verbose_name=_(u'Name'))
    author = models.CharField(max_length=100, db_column='bu_author',
                              verbose_name=_(u'Author'))
    publisher = models.CharField(max_length=100, db_column='bu_verlag',
                                 verbose_name=_(u'Publisher'))
    edition = models.CharField(max_length=100, db_column='bu_auflage',
                               verbose_name=_(u'Edition'))
    language = models.ForeignKey('Language', db_column='bu_sprid',
                                 verbose_name=_(u'Language'))
    isbn10 = models.CharField(max_length=10, db_column='bu_isbn10',
                              blank=True, null=True,
                                verbose_name=_(u'ISBN-10'))
    isbn13 = models.CharField(max_length=13, db_column='bu_isbn13',
                              blank=True, null=True,
                              verbose_name=_(u'ISBN-13'))
    created_by = models.ForeignKey(User, db_column='bu_crid',
                                   null=True, related_name='book_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='bu_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='bu_updid',
                                   null=True, related_name='book_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='bu_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'buch'
        verbose_name = _(u'Book')
        verbose_name_plural = _(u'Books')

    def __unicode__(self):
        return self.name


class BookUser(Model):

    id = models.AutoField(db_column='bup_id', primary_key=True,
                          verbose_name=_(u'Id'))
    book = models.ForeignKey('Book', db_column='bup_buid',
                             verbose_name=_(u'Book'))
    user = models.ForeignKey(User, db_column='bup_userid',
                             verbose_name=_(u'User'))
    lent = models.DateTimeField(db_column='bup_geliehen',
                                verbose_name=_(u'Lent'))
    returned = models.DateTimeField(db_column='bup_zurueck',
                                    blank=True, null=True,
                                    verbose_name=_(u'Returned'))
    created_by = models.ForeignKey(User, db_column='bup_crid',
                                   null=True, related_name='bookuser_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='bup_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='bup_updid',
                                   null=True, related_name='bookuser_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='bup_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'buchperson'
        verbose_name = _(u'Book user')
        verbose_name_plural = _(u'Book users')


class Booking(Model):

    id = models.AutoField(db_column='st_id', primary_key=True,
                          verbose_name=_(u'Id'))
    title = models.CharField(db_column='st_titel', max_length=255,
                             verbose_name=_(u'Title'))
    description = models.TextField(db_column='st_bem',
                                   verbose_name=_(u'Description'))
    day = models.ForeignKey('Day', db_column='st_taid',
                            verbose_name=_(u'Day'))
    position = models.IntegerField(db_column='st_pos',
                                   verbose_name=_(u'Position'))
    project = models.ForeignKey('Project', db_column='st_prid',
                                verbose_name=_(u'Project'))
    step = models.ForeignKey('ProjectStep', db_column='st_psid',
                             blank=True, null=True,
                             verbose_name=_(u'Project step'))
    issue = models.ForeignKey(Issue, db_column='st_tiid', blank=True,
                              null=True, verbose_name=_(u'Issue'))
    from_time = models.TimeField(db_column='st_von',
                                 blank=True, null=True,
                                 verbose_name=_(u'Start'))
    to_time = models.TimeField(db_column='st_bis',
                               blank=True, null=True,
                               verbose_name=_(u'End'))
    #from_time = models.DecimalField(db_column='st_von',
                                    #max_digits=5, decimal_places=3,
                                    #blank=True, null=True,
                                    #verbose_name=_(u'From'))
    #to_time = models.DecimalField(db_column='st_bis',
                                  #max_digits=5, decimal_places=3,
                                  #blank=True, null=True,
                                  #verbose_name=_(u'To'))
    duration = models.DecimalField(db_column='st_std', max_digits=7,
                                   decimal_places=3,
                                   verbose_name=_(u'Duration'))
    location = models.CharField(db_column='st_ort', max_length=250,
                                blank=True, null=True,)
    invoice_no = models.IntegerField(db_column='st_rnr',
                                     blank=True, null=True,
                                     verbose_name=_(u'Invoice no.'))
    coefficient = models.DecimalField(db_column='st_faktor', max_digits=4,
                                      decimal_places=2, blank=True, null=True,
                                      verbose_name=_(u'External coefficient'))
    external_coefficient = models.DecimalField(db_column='st_pfaktor',
                                               max_digits=4, decimal_places=2,
                                               blank=True, null=True,
                                               verbose_name=_(u'Coefficient'))
    created_by = models.ForeignKey(User, db_column='st_crid',
                                   null=True,
                                   related_name='booking_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='st_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='st_updid',
                                   null=True,
                                   related_name='booking_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='st_upddate',
                                   verbose_name=_(u'Updated'))


    #status = models.ForeignKey('BookingStatus', db_column='st_sts')

    invoice_no.invoice_filter = True

    _is_starred = None

    class Meta:
        db_table = u'stunde'
        permissions = (
            ('can_write', ''),
            ('can_read', ''),
            )
        verbose_name = _(u'Booking')
        verbose_name_plural = _(u'Bookings')

    #def __unicode__(self):
        #return self.get_title()

    def copy(self, user):
        copy = Booking()
        for f in self._meta.fields:
            if f.attname in ['id', 'created', 'updated', 'created_by',
                             'updated_by']:
                continue
            raw_value = getattr(self, f.attname)
            setattr(copy, f.attname, raw_value)
        date = self.day.date + datetime.timedelta(days=1)
        copy.day = user.account.get_day(date)
        copy.created_by = user
        copy.created = datetime.datetime.now()
        copy.updated_by = user
        copy.updated = datetime.datetime.now()
        return copy

    def is_starred(self):
        """Is the booking starred?

        :returns: ``True`` or ``False``
        """
        if self._is_starred is not None:
            return self._is_starred
        account = Account.current_user_account
        self._is_starred = account is not None \
            and self.id in account.starred_bookings
        return self._is_starred

    @models.permalink
    def get_absolute_url(self):
        #return '/time/edit/%d' % self.id
        #return reverse('inhouse.views.edit_booking', self.id, [])
        return ('inhouse.views.edit_booking', [str(self.id)])

    def get_closing_reason_tuple(self):
        """Return one ore more reasons, why the booking is closed.

        :returns: Tuple with strings
        """
        reasons = []
        if not self.is_closed():
            return reasons
        if self.day.locked:
            reasons.append(_(u'The day is locked.'))
        if self.project.is_closed():
            reasons.append(_(u'The project is closed or inactive.'))
        if self.step.is_closed():
            reasons.append(_(u'The projectstep is closed.'))
        return tuple(reasons)

    def get_closing_reason_string(self, sep='<br />'):
        """Return the closing reason(s) as one single string.

        :returns: String
        """
        data = self.get_closing_reason_tuple()
        if '<' in sep:
            frmt = cgi.escape
        else:
            frmt = lambda x: x
        return sep.join(frmt(part) for part in data if part is not None)


    def get_description(self):
        """Returns either the issue description or the issue description.

        :returns: Description as string
        """
        if self.issue:
            retval = self.issue.description
        else:
            retval = self.description
        return retval or _(u'No description')

    def get_key(self):
        if self.project:
            return '%s-%s' % (self.project.key, self.id)
        else:
            return str(self.id)

    def get_latest_history(self):
        """Get the latest history object.

        :returns: :class:`BookingHistory`
        """
        histories = BookingHistory.objects.filter(booking_id=self.id)
        histories = histories.filter('-created')
        retval = histories[0]
        return retval

    def get_title(self):
        """Returns ether the booking title, or the ticket title and number.

        :returns: Booking title as string
        """
        if self.issue:
            retval = self.issue.get_title()
        else:
            retval = self.title
        return retval or _(u'No title')

    def historize(self, action):
        hist = BookingHistory()
        hist.action = action
        hist.booking_id = self.id
        hist.created = datetime.datetime.now()
        hist.updated = datetime.datetime.now()
        for f in self._meta.fields:
            if f.attname in ['id', 'created', 'updated']:
                continue
            raw_value = getattr(self, f.attname)
            setattr(hist, f.attname, raw_value)
        return hist

    def is_closed(self):
        """Is the booking editable?

        :returns: ``True`` or ``False``
        """
        if (self.project.is_closed() or self.day.locked
            or self.step.is_closed()):
            return True
        return False

    def next_position(self):
        """Set the next available position, depending on the day."""
        bookings = Booking.objects.filter(day=self.day)
        self.position = (bookings.aggregate(models.Max('position'))[
            'position__max'] or 0) + 1

    def revert(self, history):
        """Copy values from a history instance.

        :param history: A :class:`History` instance
        """
        for f in history._meta.fields:
            if f.attname in ['id', 'created', 'updated']:
                continue
            raw_value = getattr(history, f.attname)
            setattr(self, f.attname, raw_value)
        self.updated = datetime.datetime.now()

    def set_issue(self, tracker_id, external_id):
        tracker = Tracker.objects.filter(id=tracker_id)
        issue = Issue.by_tracker_id(tracker, external_id)
        self.issue = issue

    def split_duration(self):
        """Split the duration into hours and minutes.

        :returns: Tuple with hours and minutes
        """
        hours = self.duration // 60
        minutes = self.duration % 60
        return int(hours), int(minutes)


def delete_booking_trigger(sender, instance, **kwds):
    history = instance.historize(HISTORY_ACTION_DELETE)
    history.save(user=history.created_by)
    cache.delete('booking:%d' % instance.id)


def save_booking_trigger(sender, instance, **kwds):
    query = BookingHistory.objects.filter(booking_id=instance.id)
    if query.count() == 0:
        action = HISTORY_ACTION_ADD
    else:
        action = HISTORY_ACTION_UPDATE
    history = instance.historize(action)
    history.save(user=history.created_by)
    # Delete cache entries for booking links, as the data could have been
    # changed.
    cache.delete('booking:%d' % instance.id)

models.signals.pre_delete.connect(delete_booking_trigger, sender=Booking)
models.signals.post_save.connect(save_booking_trigger, sender=Booking)


class BookingHistory(Model):
    """History for booking entries."""

    id = models.AutoField(db_column='h_id', primary_key=True,
                          verbose_name=_(u'Id'))
    action = models.CharField(db_column="h_action", max_length=1,
                              verbose_name=_(u"Action"))
    #booking = models.ForeignKey('Booking', db_column='hst_stid',
                                #verbose_name=_(u'Booking'))
    booking_id = models.IntegerField(db_column='hst_stid',
                                     verbose_name=_(u'Booking id'))
    title = models.CharField(db_column='hst_titel', max_length=255,
                             verbose_name=_(u'Title'))
    description = models.TextField(db_column='hst_bem',
                                   verbose_name=_(u'Description'))
    day = models.ForeignKey('Day', db_column='hst_taid',
                            verbose_name=_(u'Day'))
    position = models.IntegerField(db_column='hst_pos',
                                   verbose_name=_(u'Position'))
    project = models.ForeignKey('Project', db_column='hst_prid',
                                verbose_name=_(u'Project'))
    step = models.ForeignKey('ProjectStep', db_column='hst_psid',
                             blank=True, null=True,
                             verbose_name=_(u'Project step'))
    issue = models.ForeignKey(Issue, db_column='hst_tiid', blank=True,
                              null=True, verbose_name=_(u'Issue'))
    #from_time = models.DecimalField(db_column='hst_von',
                                    #max_digits=5, decimal_places=3,
                                    #blank=True, null=True,
                                    #verbose_name=_(u'From'))
    #to_time = models.DecimalField(db_column='hst_bis',
                                  #max_digits=5, decimal_places=3,
                                  #blank=True, null=True,
                                  #verbose_name=_(u'To'))
    from_time = models.TimeField(db_column='hst_von',
                                 blank=True, null=True,
                                 verbose_name=_(u'Start'))
    to_time = models.TimeField(db_column='hst_bis',
                               blank=True, null=True,
                               verbose_name=_(u'End'))
    duration = models.DecimalField(db_column='hst_std', max_digits=7,
                                   decimal_places=3,
                                   verbose_name=_(u'Duration'))
    location = models.CharField(db_column='hst_ort', max_length=250,
                                blank=True, null=True,)
    invoice_no = models.IntegerField(db_column='hst_rnr',
                                     blank=True, null=True,
                                     verbose_name=_(u'Invoice no.'))
    coefficient = models.DecimalField(db_column="hst_faktor", max_digits=4,
                                      decimal_places=2, blank=True, null=True,
                                      verbose_name=_(u'External coefficient'))
    external_coefficient = models.DecimalField(db_column="hst_pfaktor",
                                               max_digits=4, decimal_places=2,
                                               blank=True, null=True,
                                               verbose_name=_(u"Coefficient"))
    created_by = models.ForeignKey(User, db_column='h_crid',
                                   null=True,
                                   related_name='bookinghistory_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='h_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='h_updid',
                                   null=True,
                                   related_name='bookinghistory_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='h_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'hst_stunde'
        verbose_name = _(u'Booking history')
        verbose_name_plural = _(u'Booking histories')

    @classmethod
    def get_by_booking_id(cls, id):
        """Return a :class:`BookingHistory` instance by it`s booking id.

        :param id: Booking id

        :returns: :class:`BookingHistory` instance
        """
        query = BookingHistory.objects.filter(booking_id=id)
        query = query.order_by('-created')
        return query[0]

    @property
    def booking(self):
        """Return the corresponding booking object.

        As whe cannot use a normal foreign key, we can only store the booking
        id, and have to select the object by hand.

        :returns: :class:`Booking` instance
        """
        query = Booking.objects.filter(id=self.booking_id)
        return query[0]

    def get_action_title(self):
        """Returns a readable format of the action id.

        :returns: String
        """
        return HISTORY_ACTIONS[self.action]

    def get_description(self):
        """Returns either the issue description or the issue description.

        :returns: Description as string
        """
        if self.issue:
            retval = self.issue.description
        else:
            retval = self.description
        return retval or _(u'No description')

    def get_title(self):
        """Returns the title of a booking entry.

        :returns: Issue number and title or booking title.
        """
        if self.issue:
            retval = u'#%d %s' % (self.issue.no, self.issue.title)
        else:
            retval = self.title
        return retval or _(u'No title')


#class BookingStatus(Model):

    #id = models.AutoField(db_column='sts_id', primary_key=True,
                          #verbose_name=_(u'Id'))
    #name = models.CharField(db_column='sts_kbez', max_length=100,
                            #unique=True, verbose_name=_(u'Name'))
    #description = models.CharField(max_length=255, db_column='sts_bez',
                                   #blank=True, null=True,
                                   #verbose_name=_(u'Description'))

    #class Meta:
        #db_table = u'k_buchungsstatus'
        #verbose_name = _(u'Booking status')
        #verbose_name_plural = _(u'Booking status')



class CommissionStatus(Model):

    id = models.AutoField(db_column='bs_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='bs_kbez', max_length=100, unique=True,
                            verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='bs_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    class Meta:
        db_table = u'k_beauftragungsstatus'
        ordering = ('name',)
        verbose_name = _(u'Commission status')
        verbose_name_plural = _(u'Commission status')

    def __unicode__(self):
        return self.name


class Communication(Model):

    id = models.AutoField(db_column='kom_id', primary_key=True,
                          verbose_name=_(u'Id'))
    email = models.EmailField(db_column='kom_email', verbose_name=_(u'E-Mail'))
    phone_landline = models.CharField(db_column='kom_tel1', max_length=40,
                                      blank=True, null=True,
                                      verbose_name=_(u'Phone no. (landline)'))
    phone_mobile = models.CharField(db_column='kom_tel2', max_length=40,
                                    blank=True, null=True,
                                    verbose_name=_(u'Phone no. (mobile)'))
    fax = models.CharField(db_column='kom_fax', max_length=40,
                           blank=True, null=True,
                           verbose_name=_(u'Fax no.'))
    url = models.URLField(db_column='kom_url', max_length=200,
                          blank=True, null=True,
                          verbose_name=_(u'URL'))
    created_by = models.ForeignKey(User, db_column='kom_crid',
                                   null=True,
                                   related_name='communication_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='kom_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='kom_updid',
                                   null=True,
                                   related_name='communication_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='kom_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'kommunikation'
        verbose_name = _(u'Communication data')
        verbose_name_plural = _(u'Communication data')

    def __unicode__(self):
        return self.get_as_string(', ')

    def get_as_string(self, sep='<br />'):
        """Return the communication data as one single string.

        :param sep: Separator to use.
        :returns: Single string with data.
        """
        data = self.get_tuple()
        if '<' in sep:
            frmt = cgi.escape
        else:
            frmt = lambda x: x
        return sep.join(frmt(part) for part in data if part is not None)

    def get_tuple(self):
        """Return the communication data as tuple elements.

        :returns: Tuple with data
        """
        t = []
        if self.email:
            t.append(self.email)
        if self.phone_landline:
            t.append(self.phone_landline)
        if self.phone_mobile:
            t.append(self.phone_mobile)
        if self.fax:
            t.append(self.fax)
        if self.url:
            t.append(self.url)
        return tuple(t)


class Company(Model):

    id = models.AutoField(db_column='fir_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(max_length=400, db_column='fir_name',
                             verbose_name=_(u'Name'))
    description = models.TextField(db_column='fir_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))
    address = models.ForeignKey('Address', db_column='fir_adrid',
                                verbose_name=_(u'Address'))
    communication = models.ForeignKey('Communication', db_column='fir_komid',
                                      verbose_name=_(u'Communication data'))
    bank = models.CharField(db_column='fir_bbez', max_length=100,
                            blank=True, null=True,
                            verbose_name=_(u'Bank'))
    bank_code = models.CharField(db_column='fir_blz', max_length=8,
                                 blank=True, null=True,
                                 verbose_name=_(u'Bank code no.'))
    account_no = models.CharField(db_column='fir_kto', max_length=10,
                                  blank=True, null=True,
                                  verbose_name=_(u'Account no.'))
    invoice_no = models.IntegerField(db_column='fir_renr',
                                     default=0,
                                     verbose_name=_(u'Invoice no.'))
    created_by = models.ForeignKey(User, db_column='fir_crid',
                                   null=True, related_name='company_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='fir_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='fir_updid',
                                   null=True, related_name='company_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='fir_upddate',
                                   verbose_name=_(u'Updated'))

    # bbez, mwa, mwb, aknr


    class Meta:
        db_table = u'firma'
        verbose_name = _(u'Company')
        verbose_name_plural = _(u'Companies')

    def __unicode__(self):
        return self.name


class Contact(Model):

    id = models.AutoField(db_column='as_id', primary_key=True,
                          verbose_name=_(u'Id'))
    salutation = models.ForeignKey('Salutation', blank=True, null=True,
                                   db_column='as_anid',
                                   verbose_name=_(u'Salutation'))
    title = models.CharField(db_column='as_titel', max_length=10,
                             blank=True, null=True,
                             verbose_name=_(u'Title'))
    first_name = models.CharField(db_column='as_vname', max_length=30,
                                  verbose_name=_(u'First name'))
    last_name = models.CharField(db_column='as_nname', max_length=30,
                                 verbose_name=_(u'Surname'))
    description = models.TextField(db_column='as_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))
    customer = models.ForeignKey('Customer', db_column='as_knid',
                                 verbose_name=_(u'Customer'))
    position = models.IntegerField(db_column='as_lfdnr',
                                   verbose_name=_(u'Position'))
    department = models.CharField(db_column='as_abteilung', max_length=30,
                                  blank=True, null=True,
                                  verbose_name=_(u'Department'))
    address = models.ForeignKey('Address', db_column='as_adrid',
                                blank=True, null=True,
                                verbose_name=_(u'Address'))
    communication = models.ForeignKey('Communication', db_column='as_komid',
                                      verbose_name=_(u'Communication data'))
    birthday = models.DateField(db_column='as_gebdat', blank=True, null=True,
                                verbose_name=_(u'Birthday'))
    created_by = models.ForeignKey(User, db_column='as_crid',
                                   null=True, related_name='contact_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='as_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='as_updid',
                                   null=True, related_name='contact_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='as_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'ansprech'
        verbose_name = _(u'Contact')
        verbose_name_plural = _(u'Contacts')

    @property
    def name(self):
        return u' '.join([self.firstname or u'', self.lastname or u''])


class Country(Model):

    id = models.AutoField(db_column='la_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='la_cid', max_length=100, unique=True,
                            verbose_name=_(u'Name'))
    printable_name = models.CharField(db_column='la_kbez', max_length=100,
                                      verbose_name=_(u'Printable name'))
    num_code = models.PositiveSmallIntegerField(db_column='la_nr',
                                                unique=True,
                                                verbose_name=_(u'Numeric code'))
    iso2 = models.CharField(db_column='la_iso2', max_length=2, unique=True,
                            verbose_name=_(u'CID'))
    iso3 = models.CharField(db_column='la_iso3', max_length=3, unique=True,
                            verbose_name=_(u'CID'))
    dial_code = models.CharField(db_column='la_vorwahl', max_length=10,
                                 null=True,
                                 verbose_name=_(u'Dial code'))

    class Meta:
        db_table = u'k_land'
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')

    def __unicode__(self):
        return self.printable_name


class Customer(Model):

    id = models.AutoField(db_column='kn_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name1 = models.CharField(max_length=400, db_column='kn_name1',
                             verbose_name=_(u'Name'))
    name2 = models.CharField(max_length=200, db_column='kn_name2',
                             blank=True, null=True,
                             verbose_name=_(u'Name'))
    name3 = models.CharField(max_length=200, db_column='kn_name3',
                             blank=True, null=True,
                             verbose_name=_(u'Name'))
    salutation = models.ForeignKey('Salutation', blank=True, null=True,
                                   db_column='kn_anid',
                                   verbose_name=_(u'Salutation'))
    address = models.ForeignKey('Address', db_column='kn_adrid',
                                verbose_name=_(u'Address'))
    communication = models.ForeignKey('Communication', db_column='kn_komid',
                                      blank=True, null=True,
                                      verbose_name=_(u'Communication data'))
    language = models.ForeignKey('Language', db_column='kn_sprid',
                                 verbose_name=_(u'Language'))
    day_rate = models.DecimalField(db_column='kn_tagessatz', max_digits=14,
                                   decimal_places=2, blank=True, null=True,
                                   verbose_name=_(u'Daily rate'))
    created_by = models.ForeignKey(User, db_column='kn_crid',
                                   null=True, related_name='customer_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='kn_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='kn_updid',
                                   null=True, related_name='customer_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='kn_upddate',
                                   verbose_name=_(u'Updated'))

    objects = managers.CustomerManager()

    # zpoa, tlx, loe, fre1, fre2, fre3, debnr

    class Meta:
        db_table = u'kunde'
        verbose_name = _(u'Customer')
        verbose_name_plural = _(u'Customers')

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return u' '.join([self.name1 or u'', self.name2 or u'',
                          self.name3 or u''])

    def has_bookable_projects(self, user=None):
        ids = set()
        query = Project.objects.get_by_customer(self, True, user)
        for project in query:
            if project.get_project_steps(active_only=True).count() > 0:
                ids.add(project.id)
        query = Project.objects.filter(id__in=ids)
        return query.count() > 0


class Day(Model):

    id = models.AutoField(db_column='ta_id', primary_key=True,
                          verbose_name=_(u'Id'))
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    date = models.DateField(db_column='ta_dat',
                            verbose_name=_(u'Date'),)
    locked = models.BooleanField(db_column='ta_sperr', default=False,
                                 verbose_name=_(u'Locked?'),)
    created_by = models.ForeignKey(User, db_column='ta_crid',
                                   null=True, related_name='day_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='ta_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='ta_updid',
                                   null=True, related_name='day_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='ta_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'tag'
        verbose_name = _(u'Day')
        verbose_name_plural = _(u'Days')

    def __unicode__(self):
        return self.slugify()

    @classmethod
    def new(cls, date, user):
        day = cls()
        day.date = date
        day.user = user
        #if group_id:
            #day.group = group_id
        #else:
            #day.group = Day.objects.filter(account=account)\
               #.aggregate(models.Max("group")).get("group__max") + 1
        return day

    def get_booking_sum(self):
        """Returns the sum of all bookings for a day (per user).

        :returns: Decimal value
        """
        query = Booking.objects.filter(day=self).aggregate(
            models.Sum('duration'))
        return query['duration__sum'] or 0

    def slugify(self):
        """Returns a slugified string of a day.

        :returns: String
        """
        return self.date.strftime('%Y/%m/%d')


#class DefaultProject(Model):

    #id = models.AutoField(db_column='sp_id', primary_key=True)
    #user = None
    #tracker = None
    #project = None


class Department(Model):

    id = models.AutoField(db_column='abt_id', primary_key=True)
    name = models.CharField(max_length=100, db_column='abt_kbez',
                            unique=True, verbose_name=_(u'Name'))
    created_by = models.ForeignKey(User, db_column='abt_crid',
                                   null=True, related_name='department_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='abt_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='abt_updid',
                                   null=True, related_name='department_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='abt_upddate',
                                   verbose_name=_(u'Updated'))

    objects = managers.DepartmentManager()

    class Meta:
        db_table = u'abteilung'
        verbose_name = _(u'Department')
        verbose_name_plural = _(u'Departments')

    def __unicode__(self):
        return self.name


class DepartmentUser(Model):

    id = models.AutoField(db_column='ppg_id', primary_key=True,
                          verbose_name=_(u'Id'),)
    department = models.ForeignKey('Department', db_column='ppg_abtid')
    user = models.ForeignKey(User, db_column='abt_userid')
    created_by = models.ForeignKey(User, db_column='ppg_crid',
                                   null=True,
                                   related_name='departmentuser_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='ppg_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='ppg_updid',
                                   null=True,
                                   related_name='departmentuser_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='ppg_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'abteilungnutzer'
        verbose_name = _(u'Department member')
        verbose_name_plural = _(u'Department members')

    def __unicode__(self):
        return u'%s:%s' % (self.department, self.user)


class Hardware(Model):

    id = models.AutoField(db_column='hw_id', primary_key=True,
                          verbose_name=_(u'Id'),)
    name = models.CharField(db_column='hw_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    manufacturer = models.ForeignKey('Manufacturer',
                                     db_column='hw_herid')
    group = models.ForeignKey('HardwareGroup', db_column='hw_hwgid')
    model = models.CharField(db_column='hw_model', max_length=100,
                             verbose_name=_(u'Model'))
    inventory_no = models.CharField(db_column='hw_inventar',
                                    max_length=100,
                                    verbose_name=_(u'Inventory no.'))
    serial_no = models.CharField(db_column='hw_seriennr',max_length=100,
                                 verbose_name=_(u'Serial no.'))
    created_by = models.ForeignKey(User, db_column='hw_crid',
                                   null=True,
                                   related_name='hardware_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='hw_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='hw_updid',
                                   null=True,
                                   related_name='hardware_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='hw_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'hardware'
        verbose_name = _(u'Hardware')
        verbose_name_plural = _(u'Hardware')


class HardwareGroup(Model):

    id = models.AutoField(db_column='hwg_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='hwg_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='hwg_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))
    created_by = models.ForeignKey(User, db_column='hwg_crid',
                                   null=True,
                                   related_name='hardwaregroup_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='hwg_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='hwg_updid',
                                   null=True,
                                   related_name='hardwaregroup_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='hwg_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'hardwaregruppe'
        verbose_name = _(u'Hardware group')
        verbose_name_plural = _(u'Hardware groups')

    def __unicode__(self):
        return self.name


class HardwareUser(Model):

    id = models.AutoField(db_column='hwp_id', primary_key=True,
                          verbose_name=_(u'Id'))
    hardware = models.ForeignKey('Hardware', db_column='hwp_hwid',
                                 verbose_name=_(u'Hardware'))
    user = models.ForeignKey(User, db_column='hwp_userid',
                             verbose_name=_(u'User'))
    created_by = models.ForeignKey(User, db_column='hwp_crid',
                                   null=True,
                                   related_name='hardwareuser_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='hwp_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='hwp_updid',
                                   null=True,
                                   related_name='hardwareuser_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='hwp_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'personhardware'
        verbose_name = _(u'User hardware')
        verbose_name_plural = _(u'User hardware')

    def __unicode__(self):
        return u'%s:%s' % (self.hardware, self.user)


class Language(Model):

    id = models.AutoField(db_column='spr_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(max_length=100, db_column='spr_kbez',
                            unique=True, verbose_name=_(u'Name'))
    cid = models.CharField(max_length=2, db_column='spr_cid',
                           unique=True, verbose_name=_(u'CID'))

    class Meta:
        db_table = u'k_sprache'
        verbose_name = _(u'Language')
        verbose_name_plural = _(u'Languages')

    def __unicode__(self):
        return self.name


class Manufacturer(Model):

    id = models.AutoField(db_column='her_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='her_kbez', max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    address = models.ForeignKey('Address', db_column='her_adrid',
                                null=True, blank=True,
                                verbose_name=_(u'Address'))
    communication = models.ForeignKey('Communication', db_column='her_komid',
                                      blank=True, null=True,
                                      verbose_name=_(u'Communication data'))
    created_by = models.ForeignKey(User, db_column='her_crid',
                                   null=True,
                                   related_name='manufacturer_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='her_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='her_updid',
                                   null=True,
                                   related_name='manufacturer_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='her_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'hersteller'
        verbose_name = _(u'Manufacturer')
        verbose_name_plural = _(u'Manufacturers')

    def __unicode__(self):
        return self.name


class Message(Model):

    id = models.AutoField(db_column='msg_id', primary_key=True,
                          verbose_name=_(u'Id'))

    # TODO ...


    created_by = models.ForeignKey(User, db_column='msg_crid',
                                   null=True,
                                   related_name='message_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='msg_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='msg_updid',
                                   null=True,
                                   related_name='message_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='msg_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'nachricht'
        verbose_name = _(u'Message')
        verbose_name_plural = _(u'Messages')


class News(Model):

    id = models.AutoField(db_column='neu_id', primary_key=True)
    title = models.CharField(max_length=200, db_column='neu_titel')
    message = models.TextField(db_column='neu_text')
    valid_from = models.DateField(db_column='neu_gueltig_ab', null=True)
    valid_to = models.DateField(db_column='neu_gueltig_bis', null=True,
                                blank=True)
    created_by = models.ForeignKey(User, db_column='neu_crid',
                                   null=True, related_name='news_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='neu_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='neu_updid',
                                   null=True, related_name='news_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='neu_upddate',
                                   verbose_name=_(u'Updated'))

    objects = managers.NewsManager()

    class Meta:
        db_table = u'neuigkeit'
        verbose_name = _(u'News')
        verbose_name_plural = _(u'News')


class NewsGroup(Model):

    id = models.AutoField(db_column='neg_id', primary_key=True,
                          verbose_name=_(u'Id'))
    news = models.ForeignKey('News', db_column='neg_neuid',
                             verbose_name=_(u'News'))
    group = models.ForeignKey(Group, db_column='neg_groupid',
                              verbose_name=_(u'Group'))
    priority = models.IntegerField(db_column='neg_prio',
                                   choices=PRIORITY_CHOICES,
                                   default=1,
                                   verbose_name=_(u'Priority'))
    created_by = models.ForeignKey(User, db_column='neg_crid',
                                   null=True,
                                   related_name='newsgroup_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='neg_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='neg_updid',
                                   null=True,
                                   related_name='newsgroup_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='neg_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'neuigkeitgruppe'
        verbose_name = _(u'News group')
        verbose_name_plural = _(u'News groups')


class Project(Model):

    id = models.AutoField(db_column='pr_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='pr_name', max_length=80,
                            unique=True,
                            verbose_name=_(u'Name'))
    key = models.CharField(db_column='pr_kurz', max_length=12,
                           unique=True, verbose_name=_(u'Key'))
    image = models.ImageField(db_column='pr_bild', blank=True, null=True,
                              upload_to='projects',
                              verbose_name=_(u'Image'))
    description = models.TextField(db_column='pr_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))
    customer = models.ForeignKey('Customer', db_column='pr_knid',
                                 verbose_name=_(u'Customer'))
    company = models.ForeignKey('Company', db_column='pr_firid',
                                blank=True, null=True,
                                verbose_name=_(u'Company'))
    contact = models.ForeignKey('Contact', db_column='pr_asid',
                                blank=True, null=True,
                                verbose_name=_(u'Contact'))
    type = models.ForeignKey('ProjectType', db_column='pr_prtid',
                             verbose_name=_(u'Type'))
    status = models.ForeignKey('ProjectStatus', db_column='pr_prsid',
                               verbose_name=_(u'Status'))
    master = models.ForeignKey('Project', db_column='pr_erstprid',
                               blank=True, null=True,
                               verbose_name=_(u'Master project'))
    department = models.ForeignKey('Department', db_column='pr_abtid',
                                   blank=True, null=True,
                                   verbose_name=_(u'Department'))
    manager = models.ForeignKey(User, db_column='pr_leitung', blank=True,
                                null=True, verbose_name=_(u'Project Manager'))
    billing_type = models.ForeignKey('BillingType', db_column='pr_abaid',
                                     blank=True, null=True,
                                     verbose_name=_(u'Billing type'))
    commission_status = models.ForeignKey('CommissionStatus',
                                          db_column='pr_bsid',
                                          blank=True, null=True,
                                          verbose_name=_(u'Commission status'))
    coefficient_saturday = models.DecimalField(
        db_column='pr_faktorsamstag',
        verbose_name=_(u'Coefficient (saturday)'),
        max_digits=8, decimal_places=2, default=1)
    coefficient_sunday = models.DecimalField(
        db_column='pr_faktorsonntag',
        verbose_name=_(u'Coefficient (sunday)'),
        max_digits=8, decimal_places=2, default=1)
    created_by = models.ForeignKey(User, db_column='pr_crid',
                                   null=True, related_name='project_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='pr_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='pr_updid',
                                   null=True, related_name='project_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='pr_upddate',
                                   verbose_name=_(u'Updated'))

    #
    department.department_filter = True

    objects = managers.ProjectManager()

    # intnummer

    class Meta:
        db_table = u'projekt'
        ordering = ('id',)
        verbose_name = _(u'Project')
        verbose_name_plural = _(u'Projects')

    def __unicode__(self):
        return self.name

    @classmethod
    def copy(cls, other, name=None):
        new = Project()
        if name is None:
            new.name = u'%s \'%s\'' % (_(u'Copy of'), other.name)
        else:
            new.name = name
        new.key = u''
        new.description = u''
        new.customer = other.customer
        new.company = other.company
        new.contact = other.contact
        new.type = other.type
        new.status = other.status
        new.department = other.department
        new.manager = other.manager
        new.billing_type = other.billing_type
        new.commission_status = other.commission_status
        new.coefficient_saturday = other.coefficient_saturday
        new.coefficient_sunday = other.coefficient_sunday
        return new

    @models.permalink
    def get_absolute_url(self):
        return ('inhouse.views.show_project', [str(self.id)])

    def get_coefficient(self, step=None, day=None):
        """Returns the billing coefficient for each booking.

        :param step:
        :param day:
        :returns: Coefficient as integer/float
        """
        co_x = 1
        co_y = 1
        if day:
            if day.date.weekday() == calendar.SATURDAY:
                if self.coefficient_saturday:
                    co_x = self.coefficient_saturday
                else:
                    co_x = DEFAULT_COEFFICIENT_SATURDAY
            elif day.date.weekday() == calendar.SUNDAY:
                if self.coefficient_sunday:
                    co_x = self.coefficient_sunday
                else:
                    co_x = DEFAULT_COEFFICIENT_SUNDAY
        if step and step.coefficient:
            co_y = step.coefficient
        return co_x * co_y

    def get_description(self):
        """Return the description or an alternate string.

        :returns: Description or default string
        """
        if self.description:
            return self.description
        else:
            return _(u'No description')

    def get_project_steps(self, active_only=True):
        query = ProjectStep.objects.filter(project=self)
        if active_only:
            query = query.filter(status__in=(STEP_STATUS_OPEN,))
        query = query.order_by('position')
        return query

    def get_members(self):
        query = User.objects.filter(projectuser__project=self)
        return query

    def get_trackers(self):
        query = ProjectTracker.objects.filter(project=self)
        return query

    def has_trackers(self):
        return self.get_trackers().count() > 0

    def is_closed(self):
        return self.status.id in PROJECT_INACTIVE_STATUS


class ProjectRate(Model):

    id = models.AutoField(db_column='psa_id', primary_key=True,
                          verbose_name=_(u'Id'))
    project = models.ForeignKey(Project, db_column='psa_prid',
                                verbose_name=_(u'Project'))
    valid_from = models.DateField(db_column='pps_von',
                                  verbose_name=_(u'Valid from'))
    valid_to = models.DateField(db_column='pps_bis',
                                verbose_name=_(u'Valid to'),
                                default=datetime.date(4711, 12, 31))
    hour_rate = models.DecimalField(db_column='pps_stdsatz', max_digits=14,
                                   decimal_places=2,
                                   verbose_name=_(u'Hourly rate'))
    created_by = models.ForeignKey(User, db_column='psa_crid',
                                   null=True,
                                   related_name='projectrate_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='psa_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='psa_updid',
                                   null=True,
                                   related_name='projectrate_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='psa_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'projektsatz'
        verbose_name = _(u'Projectrate')
        verbose_name_plural = _(u'Projectrates')


class ProjectUser(Model):

    id = models.AutoField(db_column='prp_id', primary_key=True)
    project = models.ForeignKey('Project', db_column='prp_prid')
    user = models.ForeignKey(User, db_column='prp_userid')
    default_step = models.ForeignKey('ProjectStep', db_column='prp_psid',
                                     blank=True, null=True)
    created_by = models.ForeignKey(User, db_column='prp_crid',
                                   null=True,
                                   related_name='projectuser_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='prp_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='prp_updid',
                                   null=True,
                                   related_name='projectuser_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='prp_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'projektperson'
        verbose_name = _(u'Project user')
        verbose_name_plural = _(u'Project users')

    def __unicode__(self):
        return u'%s:%s' % (self.project, self.user)


class ProjectUserRate(Model):

    id = models.AutoField(db_column='pps_id', primary_key=True)
    project_user = models.ForeignKey('ProjectUser', db_column='pps_prpid')
    purchase_rate = models.DecimalField(db_column='pps_ek', max_digits=14,
                                   decimal_places=2, null=True,
                                   verbose_name=_(u'Purchase rate'))
    sale_rate = models.DecimalField(db_column='pps_vk', max_digits=14,
                                   decimal_places=2, null=True,
                                   verbose_name=_(u'Sale rate'))
    hours = models.DecimalField(db_column='pps_std', max_digits=7,
                                   decimal_places=3, default=0,
                                   verbose_name=_(u'Hours'))
    hour_rate = models.DecimalField(db_column='pps_stdsatz', max_digits=14,
                                   decimal_places=2, null=True,
                                   verbose_name=_(u'Hourly rate'))
    valid_from = models.DateField(db_column='pps_von',
                                  default=datetime.datetime(1970, 1, 1))
    valid_to = models.DateField(db_column='pps_bis',
                                default=datetime.datetime(4711, 12, 31))
    created_by = models.ForeignKey(User, db_column='pps_crid',
                                   null=True,
                                   related_name='projectuserrate_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='pps_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='pps_updid',
                                   null=True,
                                   related_name='projectuserrate_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='pps_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'projektpersonsatz'
        verbose_name = _(u'Project user rate')
        verbose_name_plural = _(u'Project user rates')



class ProjectStatus(Model):

    id = models.AutoField(db_column='prs_id', primary_key=True)
    name = models.CharField(db_column='prs_kbez', max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='prs_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    class Meta:
        db_table = u'k_projektstatus'
        ordering = ('name',)
        verbose_name = _(u'Project status')
        verbose_name_plural = _(u'Project status')

    def __unicode__(self):
        return self.name


class ProjectStep(Model):

    id = models.AutoField(db_column='ps_id', primary_key=True)
    name = models.CharField(db_column='ps_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='ps_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))
    project = models.ForeignKey('Project', db_column='ps_prid',
                                verbose_name=_(u'Project'))
    position = models.IntegerField(db_column='ps_pos',
                                   verbose_name=_(u'Position'))
    status = models.ForeignKey('ProjectStepStatus', db_column='ps_srtid',
                               verbose_name=_(u'Status'))
    coefficient = models.DecimalField(db_column='ps_faktor', max_digits=5,
                                      decimal_places=4, blank=True, null=True,
                                      verbose_name=_(u'Coefficient'))
    duration = models.IntegerField(db_column='ps_plandauer',
                                   blank=True, null=True,
                                   verbose_name=_(u'Duration'))
    flat_rate = models.DecimalField(db_column='ps_pauschale', max_digits=14,
                                   decimal_places=2, blank=True, null=True,
                                   verbose_name=_(u'Flatrate'))
    day_rate = models.DecimalField(db_column='ps_tagessatz', max_digits=14,
                                   decimal_places=2, blank=True, null=True,
                                   verbose_name=_(u'Daily rate'))
    created_by = models.ForeignKey(User, db_column='ps_crid',
                                   null=True,
                                   related_name='projectstep_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='ps_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='ps_updid',
                                   null=True,
                                   related_name='projectstep_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='ps_upddate',
                                   verbose_name=_(u'Updated'))

    objects = managers.ProjectStepManager()

    # intnummer

    class Meta:
        db_table = u'projektschritt'
        verbose_name = _(u'Project step')
        verbose_name_plural = _(u'Project steps')

    def __unicode__(self):
        return self.name

    @classmethod
    def copy(cls, other):
        new = ProjectStep()
        new.name = other.name
        new.description = other.description
        new.status = ProjectStepStatus.get_by_id(STEP_STATUS_OPEN)
        return new

    def is_closed(self):
        return self.status.id in PROJECT_STEP_INACTIVE_STATUS

    def is_default(self, user):
        query = ProjectUser.objects.filter(project=self.project,
                                           user=user,
                                           default_step=self.id)
        return query.count() == 1

    def next_position(self):
        """Set the next free position for a project`s step."""
        steps = ProjectStep.objects.filter(project=self.project)
        # Automatically determine the fields new position
        max = steps.aggregate(models.Max('position'))['position__max'] or 0
        self.position = max + 1


class ProjectStepTemplate(Model):
    """Defines a default step, that can be assigned with projects."""

    id = models.AutoField(db_column='pst_id', primary_key=True)
    name = models.CharField(db_column='pst_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='pst_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))
    created_by = models.ForeignKey(User, db_column='pst_crid',
                                   null=True,
                                   related_name='projectsteptemplate_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='pst_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='pst_updid',
                                   null=True,
                                   related_name='projectsteptemplate_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='pst_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'projektschritttemplate'
        verbose_name = _(u'Project step template')
        verbose_name_plural = _(u'Project step templates')


class ProjectStepStatus(Model):

    id = models.AutoField(db_column='srt_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='srt_kbez', max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='srt_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    class Meta:
        db_table = u'k_schrittstatus'
        verbose_name = _(u'Project step status')
        verbose_name_plural = _(u'Project step status')

    def __unicode__(self):
        return self.name


class ProjectTracker(Model):
    """Relation for :class:`Project` and :class:`IssueTracker`"""

    id = models.AutoField(db_column='pts_id', primary_key=True,
                          verbose_name=_(u'Id'))
    tracker = models.ForeignKey(Tracker, db_column='pts_tsyid',
                                verbose_name=_(u'Issue tracker'))
    project = models.ForeignKey('Project', db_column='pts_prid',
                                verbose_name=_(u'Project'))
    created_by = models.ForeignKey(User, db_column='pts_crid',
                                   null=True,
                                   related_name='projectracker_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='pts_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='pts_updid',
                                   null=True,
                                   related_name='projecttracker_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='pts_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'projektticketsystem'
        verbose_name = _(u'Project issue tracker')
        verbose_name_plural = _(u'Project issue tracker')

    def __unicode__(self):
        return u'%s:%s' % (self.project, self.tracker)


class ProjectType(Model):

    id = models.AutoField(db_column='prt_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='prt_kbez', max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='prt_bez',
                                   blank=True, null=True,
                                   verbose_name=_(u'Description'))

    class Meta:

        db_table = u'k_projekttyp'
        ordering = ('name',)
        verbose_name = _(u'Project type')
        verbose_name_plural = _(u'Project types')

    def __unicode__(self):
        return self.name


class Salutation(Model):

    id = models.AutoField(db_column='an_id', primary_key=True,
                          verbose_name=_(u'Id'))
    short_name = models.CharField(db_column='an_kurz', max_length=10,
                                  verbose_name=_(u'Short name'))
    name = models.CharField(db_column='an_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    letter = models.CharField(db_column='an_brf', max_length=100,
                            verbose_name=_(u'Name'))

    class Meta:
        db_table = u'k_anrede'
        verbose_name = _(u'Salutation')
        verbose_name_plural = _(u'Salutations')

    def __unicode__(self):
        return self.name


class Software(Model):

    id = models.AutoField(db_column='sw_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='sw_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    manufacturer = models.ForeignKey('Manufacturer', db_column='sw_herid',
                                     verbose_name=_(u'Manufacturer'))
    group = models.ForeignKey('SoftwareGroup', db_column='sw_swgid',
                              verbose_name=_(u'Group'))
    version = models.CharField(db_column='sw_version', max_length=20,
                               verbose_name=_(u'Version'))
    created_by = models.ForeignKey(User, db_column='sw_crid',
                                   null=True, related_name='software_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='sw_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='sw_updid',
                                   null=True, related_name='software_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='sw_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'software'
        verbose_name = _(u'Software')
        verbose_name_plural = _(u'Software')

    def __unicode__(self):
        return self.name


class SoftwareGroup(Model):

    id = models.AutoField(db_column='swg_id', primary_key=True,
                          verbose_name=_(u'Id'))
    name = models.CharField(db_column='swg_kbez', max_length=100,
                            verbose_name=_(u'Name'))
    description = models.CharField(max_length=255, db_column='swg_bez',
                                   verbose_name=_(u'Description'))
    created_by = models.ForeignKey(User, db_column='swg_crid',
                                   null=True,
                                   related_name='softwaregroup_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='swg_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='swg_updid',
                                   null=True,
                                   related_name='softwaregroup_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='swg_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'softwaregruppe'
        verbose_name = _(u'Software group')
        verbose_name_plural = _(u'Software groups')

    def __unicode__(self):
        return self.name


class SystemConfig(Model):

    pass


class Timer(Model):

    id = models.AutoField(db_column='tim_id', primary_key=True,
                          verbose_name=_(u'Id'))
    start_time = models.DateTimeField(db_column='tim_start',
                                      verbose_name=_(u'Start'))
    #end_time = models.DateTimeField(db_column='tim_ende',
                                    #blank=True, null=True,
                                    #verbose_name=_(u'Stop'))
    duration = models.IntegerField(db_column='tim_dauer',
                                   default=0,
                                   verbose_name=_(u'Duration'))
    title = models.CharField(db_column='tim_titel', max_length=255,
                             verbose_name=_(u'Title'))
    status = models.IntegerField(db_column='tim_status', choices=TIMER_CHOICES,
                                 default=1, verbose_name=_(u'Status'))
    created_by = models.ForeignKey(User, db_column='tim_crid',
                                   null=True, related_name='timer_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='tim_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='tim_updid',
                                   null=True, related_name='timer_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='tim_upddate',
                                   verbose_name=_(u'Updated'))

    class Meta:
        db_table = u'timer'
        verbose_name = _(u'Timer')
        verbose_name_plural = _(u'Timer')

    def clear(self):
        """Resets the timer."""
        self.status = TIMER_STATUS_STOPPED
        self.duration = 0

    def get_elapsed_time(self):
        if self.duration > 0:
            if self.is_active():
                return self.duration + (datetime.datetime.now() - self.start_time).seconds
            else:
                return self.duration
        else:
            if self.is_active():
                return (datetime.datetime.now() - self.start_time).seconds
            else:
                return 0

    def get_time_tuple(self):
        """Returns a split time information in hours and minutes.

        :return: Tuple with hours, minutes
        """
        minutes = self.duration / 60
        if minutes <= 15:
            # Less then 15 minutes count as 15 minutes
            return 0, 15
        h = minutes // 60
        minutes -= h * 60
        scrap = minutes % 15
        m = (minutes // 15) * 15
        if scrap >= 7.5:
            m += 15
        if m >= 60:
            h += m // 60
            m -= m % 60
        return h, m

    def is_active(self):
        """Is the timer currently active?

        :returns: ``True`` or ``False``
        """
        return self.status == TIMER_STATUS_ACTIVE

    def start(self, title=None):
        if title:
            self.title = title
        self.start_time = datetime.datetime.now()
        self.status = TIMER_STATUS_ACTIVE

    def stop(self):
        end_time = datetime.datetime.now()
        self.status = TIMER_STATUS_STOPPED
        if not self.start_time:
            self.duration = 0
        else:
            self.duration += (end_time - self.start_time).seconds


class UserConfig(Model):

    pass


class UserProfile(Model):

    id = models.AutoField(db_column='pe_id', primary_key=True,
                          verbose_name=_(u'Id'))
    user = models.ForeignKey(User, unique=True,
                             db_column='pe_userid')
    short_name = models.CharField(db_column='pe_kurz', max_length=8,
                                  unique=True, verbose_name=_(u'Short name'))
    company = models.ForeignKey('Company', db_column='pe_firid', blank=True,
                                null=True, verbose_name=_(u'Company'))
    salutation = models.ForeignKey('Salutation', blank=True, null=True,
                                   db_column='pe_anid',
                                   verbose_name=_(u'Salutation'))
    address = models.ForeignKey('Address', db_column='pe_adrid',
                                verbose_name=_(u'Address'))
    communication = models.ForeignKey('Communication', db_column='pe_komid',
                                      blank=True, null=True,
                                      verbose_name=_(u'Communication data'))
    birthday = models.DateField(db_column='pe_gebdat', blank=True, null=True,
                                verbose_name=_(u'Birthday'))
    day_rate = models.DecimalField(db_column='pe_tagkosten', max_digits=14,
                                   decimal_places=2, default=0,
                                   verbose_name=_(u'Daily rate'))
    job = models.CharField(db_column='pe_job', max_length=80, blank=True,
                           null=True, verbose_name=_(u'Job'))
    personnel_no = models.CharField(db_column='pe_personalnr', max_length=250,
                                    blank=True, null=True,
                                    verbose_name=_(u'Personell no.'))
    hours_per_week = models.DecimalField(db_column='pe_stdwoche',
                                         max_digits=14, decimal_places=2,
                                         blank=True, null=True,
                                         verbose_name=_(u'Hours per week'))
    created_by = models.ForeignKey(User, db_column='pe_crid',
                                   null=True,
                                   related_name='userprofile_creators',
                                   verbose_name=_(u'Created by'))
    created = models.DateTimeField(db_column='pe_crdate',
                                   verbose_name=_(u'Created'))
    updated_by = models.ForeignKey(User, db_column='pe_updid',
                                   null=True,
                                   related_name='userprofile_updators',
                                   verbose_name=_(u'Updated by'))
    updated = models.DateTimeField(db_column='pe_upddate',
                                   verbose_name=_(u'Updated'))
    class Meta:
        db_table = u'person'
        verbose_name = _(u'User profile')
        verbose_name_plural = _(u'User profiles')


def save_userprofile_trigger(sender, instance, **kwds):
    # Delete cache entries when user profile data gets changed.
    cache.delete('user_popup:%d' % instance.id)
    cache.delete('user:%d' % instance.id)

models.signals.post_save.connect(save_userprofile_trigger, sender=UserProfile)
