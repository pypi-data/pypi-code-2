# -*- coding: utf-8 -*-

"""Testcases for the models."""

import datetime
import time
import unittest

from django.test.client import Client

from inhouse import models


class BookingTest(unittest.TestCase):

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


class DayTest(unittest.TestCase):

    def test_slugify(self):
        day = models.Day()
        day.date = datetime.date(2010, 1, 12)
        self.assertEqual(day.slugify(), u'2010/01/12')
        day.date = datetime.date(2012, 7, 15)
        self.assertEqual(day.slugify(), u'2012/07/15')


class ProjectTest(unittest.TestCase):

    def test_is_closed(self):
        #project = models.Project()
        #project.status = models.PROJECT_STATUS_OPEN
        #self.assertEqual(project.is_closed(), False)
        #project.status = models.PROJECT_STATUS_DELETED
        #self.assertEqual(project.is_closed(), True)
        pass


class TimerTest(unittest.TestCase):

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