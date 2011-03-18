# -*- coding: utf-8 -*-

"""Testcases for the models."""

import datetime
import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from inhouse import models


class AccountTest(TestCase):

    def test_get_short_name(self):
        acc = models.Account()
        acc.first_name = u'Fooo'
        acc.last_name = u'Baaaaar'
        ret = models.Account.get_short_name(acc)
        self.assertEqual(ret, u'FoBaa')
        acc.first_name = u'F'
        acc.last_name = u'B'
        ret = models.Account.get_short_name(acc)
        self.assertEqual(ret, u'FB')

    def test_nickname(self):
        acc = models.Account()
        acc.username = u'foo_bar'
        acc.first_name = u'Foo'
        acc.last_name = u'Bar'
        self.assertEqual(acc.nickname, u'Foo Bar')
        acc.first_name = u'Foo'
        acc.last_name = None
        self.assertEqual(acc.nickname, u'foo_bar')
        acc.first_name = None
        acc.last_name = u'Bar'
        self.assertEqual(acc.nickname, u'foo_bar')
        

class AddressTest(TestCase):

    def test_get_addressstring(self):
        c = models.Country()
        c.id = 1
        c.name = u'Germany'
        adr = models.Address()
        adr.name1 = u'foo'
        adr.name2 = u'bar'
        adr.country = c
        ret = adr.get_addressstring()
        self.assertEqual(ret, u'foo<br />bar<br />')
        adr.street = u'foostreet'
        ret = adr.get_addressstring()
        self.assertEqual(ret, u'foo<br />bar<br />foostreet<br />')

    def test_get_addresstuple(self):
        c = models.Country()
        c.id = 1
        c.name = u'Germany'
        adr = models.Address()
        adr.name1 = u'Max'
        ret = adr.get_addresstuple(names_only=True)
        self.assert_(isinstance(ret, tuple))
        self.assertEqual(len(ret), 1)
        adr.name2 = u'Mustermann'
        ret = adr.get_addresstuple(names_only=True)
        self.assertEqual(len(ret), 2)
        adr.name3 = u'foo'
        ret = adr.get_addresstuple(names_only=True)
        self.assertEqual(len(ret), 3)
        adr.name4 = u'bar'
        adr.street = u'Musterstrasse'
        adr.city = u'Musterstadt'
        adr.zip_code = '12345'
        adr.country = c
        ret = adr.get_addresstuple(names_only=True)
        self.assertEqual(len(ret), 4)
        ret = adr.get_addresstuple(names_only=False)
        self.assertEqual(len(ret), 7)

    def test_get_join_name(self):
        c = models.Country()
        c.id = 1
        c.name = u'Germany'
        adr = models.Address()
        adr.name1 = u'foo1'
        adr.name2 = u'foo2'
        adr.name3 = u'foo3'
        adr.name4 = u'foo4'
        adr.country = c
        ret = adr.get_join_name()
        self.assertEqual(ret, 'foo1foo2foo3foo4')
        ret = adr.get_join_name(' ')
        self.assertEqual(ret, 'foo1 foo2 foo3 foo4')

    def test_get_join_name_html(self):
        c = models.Country()
        c.id = 1
        c.name = u'Germany'
        adr = models.Address()
        adr.name1 = u'foo1'
        adr.name2 = u'foo2'
        adr.name3 = u'foo3'
        adr.name4 = u'foo4'
        ret = adr.get_join_name_html()
        self.assertEqual(ret, 'foo1<br />foo2<br />foo3<br />foo4')


class BookingTest(TestCase):

    fixtures = ['test_data.json']

    def test_get_description(self):
        b = models.Booking()
        self.assertEqual(b.get_description(), u'No description')
        b.description = u'foobar'
        self.assertEqual(b.get_description(), u'foobar')
        i = models.Issue()
        i.title = u'foo'
        i.description = u'bar'
        b.issue = i
        self.assertEqual(b.get_description(), u'bar')

    def test_get_title(self):
        i = models.Issue()
        i.title = u'foo'
        i.no = 1
        b = models.Booking()
        self.assertEqual(b.get_title(), u'No title')
        b.title = u'bar'
        self.assertEqual(b.get_title(), u'bar')
        b.issue = i
        self.assertEqual(b.get_title(), u'#1: foo')
        im = models.Issue()
        im.title = u'foomaster'
        im.no = 2
        i.master = im
        self.assertEqual(b.get_title(), u'#1 (#2): foo')

    def test_historize(self):
        booking = models.Booking()
        booking.duration = 120
        history = booking.historize(models.HISTORY_ACTION_ADD)
        self.assertEqual(history.action, models.HISTORY_ACTION_ADD)
        self.assertEqual(booking.id, history.booking_id)
        self.assertEqual(booking.duration, history.duration)

    def test_split_duration(self):
        booking = models.Booking()
        booking.duration = 120
        self.assertEqual(booking.split_duration(), (2, 0))
        booking.duration = 125
        self.assertEqual(booking.split_duration(), (2, 5))
        booking.duration = 319
        self.assertEqual(booking.split_duration(), (5, 19))

    def test_get_key(self):
        user = User.objects.create_user('foo', 'test@example.com', 'bar')
        project = models.Project.get_by_id(1)
        project.key = u'FOO'
        day = models.Day()
        day.user = user
        day.date = datetime.date.today()
        day.save(user=user)
        b = models.Booking()
        b.project = project
        b.day = day
        b.position = 1
        b.step = models.ProjectStep.get_by_id(1)
        b.duration = 120
        b.save(user=user)
        self.assertEqual(b.get_key(), u'FOO-%s' % b.id)
        project.key = u'BAR'
        project.save(user=user)
        self.assertEqual(b.get_key(), u'BAR-%s' % b.id)


class DayTest(TestCase):

    def test_slugify(self):
        day = models.Day()
        day.date = datetime.date(2010, 1, 12)
        self.assertEqual(day.slugify(), u'2010/01/12')
        day.date = datetime.date(2012, 7, 15)
        self.assertEqual(day.slugify(), u'2012/07/15')


class ProjectTest(TestCase):

    fixtures = ['test_data.json']

    def test_is_closed(self):
        project = models.Project.get_by_id(1)
        project.status = models.ProjectStatus.get_by_id(models.PROJECT_STATUS_OPEN)
        self.assertEqual(project.is_closed(), False)
        project.status = models.ProjectStatus.get_by_id(models.PROJECT_STATUS_DELETED)
        self.assertEqual(project.is_closed(), True)

    def test_get_coefficient(self):
        p = models.Project()
        p.name = u'Foo project'
        self.assertEqual(p.get_coefficient(), 1)


class ProjectStepTest(TestCase):

    fixtures = ['test_data.json']

    def test_next_position(self):
        user = User.objects.create_user('foo', 'test@example.com', 'bar')
        # Create a new project without steps
        p = models.Project()
        p.customer = models.Customer.get_by_id(1)
        p.status = models.ProjectStatus.get_by_id(models.PROJECT_STATUS_OPEN)
        p.type = models.ProjectType.get_by_id(1)
        p.save(user=user)
        s = models.ProjectStep()
        s.project = p
        s.status = models.ProjectStepStatus.get_by_id(1)
        s.next_position()
        s.save(user=user)
        self.assertEqual(s.position, 1)
        s2 = models.ProjectStep()
        s2.project = p
        s2.status = models.ProjectStepStatus.get_by_id(1)
        s2.next_position()
        self.assertEqual(s2.position, 2)


class TimerTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_clear(self):
        timer = models.Timer()
        timer.clear()
        self.assertEqual(timer.status, models.TIMER_STATUS_STOPPED)
        self.assertEqual(timer.duration, 0)

    def test_get_time_tuple(self):
        timer = models.Timer()
        timer.duration = 4380
        hours, minutes = timer.get_time_tuple()
        self.assertEqual(hours, 1)
        self.assertEqual(minutes, 15)
        timer.duration = 540
        hours, minutes = timer.get_time_tuple()
        self.assertEqual(hours, 0)
        self.assertEqual(minutes, 15)

    def test_is_active(self):
        timer = models.Timer()
        timer.status = models.TIMER_STATUS_STOPPED
        self.assertEqual(timer.is_active(), False)
        timer.status = models.TIMER_STATUS_ACTIVE
        self.assertEqual(timer.is_active(), True)

    def test_start(self):
        timer = models.Timer()
        timer.start()
        self.assertEqual(timer.status, models.TIMER_STATUS_ACTIVE)

    def test_stop(self):
        timer = models.Timer()
        timer.stop()
        self.assertEqual(timer.status, models.TIMER_STATUS_STOPPED)
        self.assertEqual(timer.duration, 0)
        timer = models.Timer()
        timer.start()
        time.sleep(1)
        timer.stop()
        self.assertEqual(timer.status, models.TIMER_STATUS_STOPPED)
        self.assertEqual(timer.duration, 1)
