# -*- coding: latin-1 -*-
# Copyright 2010 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import random

from django.conf import settings
from django.core import urlresolvers
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from pykeg.core import kb_common
from pykeg.core import fields
from pykeg.core import stats
from pykeg.core import units
from pykeg.core import util

from pykeg.beerdb import models as bdb

"""Django models definition for the kegbot database."""

def mugshot_file_name(instance, filename):
  rand_salt = random.randrange(0xffff)
  new_filename = '%04x-%s' % (rand_salt, filename)
  return os.path.join('mugshots', instance.user.username, new_filename)

def _set_seqn_pre_save(sender, instance, **kwargs):
  if instance.seqn:
    return
  prev = sender.objects.filter(site=instance.site).order_by('-seqn')
  if not prev.count():
    seqn = 1
  else:
    seqn = prev[0].seqn + 1
  instance.seqn = seqn


class KegbotSite(models.Model):
  name = models.CharField(max_length=64, unique=True,
      help_text='A short name for this site, eg "default" or "sfo"')
  description = models.TextField(blank=True, null=True,
      help_text='Description of this site')

  def __str__(self):
    return '%s %s' % (self.name, self.description)

class UserPicture(models.Model):
  def __str__(self):
    return "%s UserPicture" % (self.user,)

  user = models.ForeignKey(User)
  image = models.ImageField(upload_to=mugshot_file_name)
  active = models.BooleanField(default=True)


class UserProfile(models.Model):
  """Extra per-User information."""
  GENDER_CHOICES = (
    ('male', 'male'),
    ('female', 'female'),
  )
  def __str__(self):
    return "profile for %s" % (self.user,)

  def FacebookProfile(self):
    if 'socialregistration' not in settings.INSTALLED_APPS:
      return None
    qs = self.user.facebookprofile_set.all()
    if qs:
      return qs[0]

  def TwitterProfile(self):
    if 'socialregistration' not in settings.INSTALLED_APPS:
      return None
    qs = self.user.twitterprofile_set.all()
    if qs:
      return qs[0]

  def MugshotUrl(self):
    if self.mugshot:
      img_url = self.mugshot.image.url
    else:
      args = ('images/unknown-drinker.png',)
      img_url = urlresolvers.reverse('site-media', args=args)
    return img_url

  user = models.OneToOneField(User)
  gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
  weight = models.FloatField()
  mugshot = models.ForeignKey(UserPicture, blank=True, null=True)

def user_post_save(sender, instance, **kwargs):
  defaults = {
    'weight': kb_common.DEFAULT_NEW_USER_WEIGHT,
    'gender': kb_common.DEFAULT_NEW_USER_GENDER,
  }
  profile, new = UserProfile.objects.get_or_create(user=instance,
      defaults=defaults)
post_save.connect(user_post_save, sender=User)


class KegSize(models.Model):
  """ A convenient table of common Keg sizes """
  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

  def __str__(self):
    return "%s [%.2f gal]" % (self.name, self.Volume().ConvertTo.USGallon)

  name = models.CharField(max_length=128)
  volume_ml = models.FloatField()


class KegTap(models.Model):
  """A physical tap of beer."""
  site = models.ForeignKey(KegbotSite)
  seqn = models.PositiveIntegerField()
  name = models.CharField(max_length=128)
  meter_name = models.CharField(max_length=128)
  ml_per_tick = models.FloatField(default=(1000.0/2200.0))
  description = models.TextField(blank=True, null=True)
  current_keg = models.ForeignKey('Keg', blank=True, null=True)
  max_tick_delta = models.PositiveIntegerField(default=100)
  temperature_sensor = models.ForeignKey('ThermoSensor', blank=True, null=True)

  def __str__(self):
    return "%s: %s" % (self.meter_name, self.name)

  def Temperature(self):
    if self.temperature_sensor:
      last_rec = self.temperature_sensor.thermolog_set.all().order_by('-time')
      if last_rec:
        return last_rec[0]
    return None

pre_save.connect(_set_seqn_pre_save, sender=KegTap)

class Keg(models.Model):
  """ Record for each installed Keg. """
  class Meta:
    unique_together = ('site', 'seqn')

  def full_volume(self):
    return self.size.Volume()

  def served_volume(self):
    drinks = Drink.objects.filter(keg__exact=self, status__exact='valid')
    tot = units.Quantity(0, units.RECORD_UNIT)
    for d in drinks:
      tot += d.Volume()
    return tot

  def remaining_volume(self):
    return self.full_volume() - self.served_volume()

  def percent_full(self):
    return float(self.remaining_volume()) / float(self.full_volume()) * 100

  def keg_age(self):
    if self.status == 'online':
      end = datetime.datetime.now()
    else:
      end = self.enddate
    return end - self.startdate

  def is_empty(self):
    return float(self.remaining_volume()) <= 0

  def tap(self):
    q = self.kegtap_set.all()
    if q:
      return q[0]
    return None

  def previous(self):
    q = Keg.objects.filter(startdate__lt=self.startdate).order_by('-startdate')
    if q.count():
      return q[0]
    return None

  def next(self):
    q = Keg.objects.filter(startdate__gt=self.startdate).order_by('startdate')
    if q.count():
      return q[0]
    return None

  def GetStats(self):
    if hasattr(self, '_stats'):
      return self._stats
    qs = self.stats.all()
    if qs:
      self._stats = qs[0].stats
    else:
      self._stats = {}
    return self._stats

  def Sessions(self):
    chunks = SessionChunk.objects.filter(keg=self)
    res = list(set(c.session for c in chunks))
    res.sort()
    return res

  def TopDrinkers(self):
    stats = self.GetStats()
    if not stats:
      return []
    ret = []
    volmap = stats.get('volume_by_drinker', {})
    for username, vol in volmap.iteritems():
      username = str(username)
      vol = float(vol)
      try:
        user = User.objects.get(username=username)
      except User.DoesNotExist:
        continue  # should not happen
      volume = units.Quantity(vol)
      ret.append((volume, user))
    ret.sort(reverse=True)
    return ret

  def __str__(self):
    return "Keg #%s - %s" % (self.id, self.type)

  site = models.ForeignKey(KegbotSite, related_name='kegs')
  seqn = models.PositiveIntegerField()
  type = models.ForeignKey(bdb.BeerType)
  size = models.ForeignKey(KegSize)
  startdate = models.DateTimeField('start date', default=datetime.datetime.now)
  enddate = models.DateTimeField('end date', default=datetime.datetime.now)
  status = models.CharField(max_length=128, choices=(
     ('online', 'online'),
     ('offline', 'offline'),
     ('coming soon', 'coming soon')))
  description = models.CharField(max_length=256, blank=True, null=True)
  origcost = models.FloatField(default=0, blank=True, null=True)
  notes = models.TextField(blank=True, null=True,
      help_text='Private notes about this keg, viewable only by admins.')

def _KegPreSave(sender, instance, **kwargs):
  keg = instance

  # We don't need to do anything if the keg is still online.
  if keg.status != 'offline':
    return

  # Determine first drink date & set keg start date to it if earlier.
  drinks = instance.drinks.all().order_by('endtime')
  if drinks:
    drink = drinks[0]
    if drink.endtime < instance.startdate:
      instance.startdate = drink.endtime

  # Determine last drink date & set keg end date to it if later.
  drinks = instance.drinks.all().order_by('-endtime')
  if drinks:
    drink = drinks[0]
    if drink.endtime > instance.enddate:
      instance.enddate = drink.endtime

pre_save.connect(_set_seqn_pre_save, sender=Keg)
pre_save.connect(_KegPreSave, sender=Keg)


class DrinkManager(models.Manager):
  def valid(self):
    return self.filter(status='valid')

class Drink(models.Model):
  """ Table of drinks records """
  class Meta:
    unique_together = ('site', 'seqn')
    get_latest_by = 'endtime'
    ordering = ('-endtime',)

  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

  def GetSession(self):
    return self.session

  def PourDuration(self):
    return self.endtime - self.starttime

  def ShortUrl(self):
    domain = Site.objects.get_current().domain
    return 'http://%s/d/%i' % (domain, self.id)

  def calories(self):
    if not self.keg or not self.keg.type:
      return 0
    cal = self.keg.type.calories_oz * self.Volume().ConvertTo.Ounce
    return cal

  def bac(self):
    bacs = self.bac_set.all()
    if bacs.count() == 1:
      return bacs[0].bac
    return 0

  def __str__(self):
    return "Drink %s by %s" % (self.id, self.user)

  objects = DrinkManager()

  site = models.ForeignKey(KegbotSite, related_name='drinks')
  seqn = models.PositiveIntegerField()

  # Ticks records the actual meter reading, which is never changed once
  # recorded.
  ticks = models.PositiveIntegerField()

  # Volume is the actual volume of the drink.  Its initial value is a function
  # of `ticks`, but it may be adjusted, eg due to calibration or mis-recording.
  volume_ml = models.FloatField()

  # Similarly, recording both the start and end times of a drink may seem odd.
  # The idea was to someday add metrics to the web page showing pour speeds.
  # This was never terribly exciting so it didn't happen, but space is cheap
  # so I'm inclined to keep the data rather than chuck it.
  #
  # For sorting and other operations requiring a single date, the endtime is
  # used.  TODO(mikey): make sure this is actually the case
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  user = models.ForeignKey(User, null=True, blank=True, related_name='drinks')
  keg = models.ForeignKey(Keg, null=True, blank=True, related_name='drinks')
  status = models.CharField(max_length=128, choices = (
     ('valid', 'valid'),
     ('invalid', 'invalid'),
     ), default = 'valid')
  session = models.ForeignKey('DrinkingSession',
      related_name='drinks', null=True, blank=True, editable=False)
  auth_token = models.CharField(max_length=256, blank=True, null=True)
  duration = models.PositiveIntegerField(blank=True, null=True)

  def _UpdateUserStats(self):
    if self.user:
      defaults = {
        'site': self.site,
      }
      stats, created = self.user.stats.get_or_create(defaults=defaults)
      stats.Update(self)

  def _UpdateKegStats(self):
    if self.keg:
      defaults = {
        'site': self.site,
      }
      stats, created = self.keg.stats.get_or_create(defaults=defaults)
      stats.Update(self)

  def PostProcess(self):
    self._UpdateUserStats()
    self._UpdateKegStats()
    SystemEvent.ProcessDrink(self)

pre_save.connect(_set_seqn_pre_save, sender=Drink)

class AuthenticationToken(models.Model):
  """A secret token to authenticate a user, optionally pin-protected."""
  class Meta:
    unique_together = ('site', 'seqn', 'auth_device', 'token_value')

  def __str__(self):
    ret = "%s: %s" % (self.auth_device, self.token_value)
    if self.user is not None:
      ret = "%s (%s)" % (ret, self.user.username)
    return ret

  site = models.ForeignKey(KegbotSite, related_name='tokens')
  seqn = models.PositiveIntegerField()
  auth_device = models.CharField(max_length=64)
  token_value = models.CharField(max_length=128)
  pin = models.CharField(max_length=256, blank=True, null=True)
  user = models.ForeignKey(User, blank=True, null=True)
  created = models.DateTimeField(auto_now_add=True)
  enabled = models.BooleanField(default=True)
  expires = models.DateTimeField(blank=True, null=True)

  def IsAssigned(self):
    return self.user is not None

  def IsActive(self):
    if not self.enabled:
      return False
    if not self.expires:
      return True
    return datetime.datetime.now() < self.expires

pre_save.connect(_set_seqn_pre_save, sender=AuthenticationToken)

class BAC(models.Model):
  """ Calculated table of instantaneous blood alcohol estimations.

  A BAC value may be added by Kegbot after each pour of a registered drinker.
  A relationship to the drink causing the calculation is stored, to ease
  lookup by Drink.

  TODO(mikey): consider making the Drink optional so that intermediate values
  can be added. Seems of dubious utility.
  TODO(mikey): if Drink is mandatory, should eliminated rectime.
  """
  user = models.ForeignKey(User)
  drink = models.ForeignKey(Drink)
  rectime = models.DateTimeField()
  bac = models.FloatField()

  def __str__(self):
    return "%s BAC at %s" % (self.user, self.drink)

  @classmethod
  def ProcessDrink(cls, d):
    """Generate the bac for a drink"""
    bac_qs = d.bac_set.all()
    if len(bac_qs):
      # Already has a recorded BAC.
      return bac_qs[0]

    if not d.user:
      return

    try:
      profile = d.user.get_profile()
    except UserProfile.DoesNotExist:
      # can't compute bac if there is no profile
      return
    if not d.keg:
      return
    if not d.keg.type.abv:
      return

    # TODO: delete/update previous bac for this drink iff exists

    # consider previously recorded bac for non-guest users
    matches = BAC.objects.filter(user=d.user).order_by('-rectime')
    prev_bac = 0
    if len(matches):
      last_bac = matches[0]
      prev_bac = util.decomposeBAC(last_bac.bac, (d.endtime - last_bac.rectime).seconds)

    now = util.instantBAC(profile.gender, profile.weight, d.keg.type.abv,
                          d.Volume().ConvertTo.Ounce)
    b = BAC(user=d.user, drink=d, rectime=d.endtime, bac=now+prev_bac)
    b.save()
    return b


def find_object_in_window(qset, when, window):
  matching = qset.filter(
      starttime__lte=when + window,
      endtime__gte=when - window
  )

  if matching:
    return matching[0]

  # Match objects ending just before the start
  earlier = qset.filter(
      endtime__gte=(when - window),
      starttime__lt=when,
  )

  if earlier:
    return earlier[0]

  # Match objects occuring just after the end
  newer = qset.filter(
      starttime__lte=(when - window),
      endtime__gt=when,
  )

  if newer:
    return newer[0]

  return None


class SessionManager(models.Manager):
  def valid(self):
    return self.filter(volume_ml__gt=kb_common.MIN_SESSION_VOLUME_DISPLAY_ML)

class AbstractChunk(models.Model):
  class Meta:
    abstract = True
    get_latest_by = 'starttime'
    ordering = ('-starttime',)

  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  volume_ml = models.FloatField(default=0)

  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

  def Duration(self):
    return self.endtime - self.startime

  def AddDrink(self, drink):
    if self.starttime > drink.starttime:
      self.starttime = drink.starttime
    if self.endtime < drink.endtime:
      self.endtime = drink.endtime
    self.volume_ml += drink.volume_ml
    self.save()


class DrinkingSession(AbstractChunk):
  """A collection of contiguous drinks. """
  class Meta:
    unique_together = ('site', 'seqn')
    get_latest_by = 'starttime'
    ordering = ('-starttime',)

  objects = SessionManager()
  site = models.ForeignKey(KegbotSite, related_name='sessions')
  seqn = models.PositiveIntegerField()

  def __str__(self):
    return "Session #%s: %s" % (self.id, self.starttime)

  def count_drinkers(self):
    return self.user_chunks.filter(user__isnull=False).count()

  def count_pints(self):
    return int(round(int(self.Volume().ConvertTo.Pint)))

  def summarize_drinkers(self):
    def fmt(user):
      url = '/drinker/%s/' % (user.username,)
      return '<a href="%s">%s</a>' % (url, user.username)
    chunks = self.user_chunks.all().order_by('-volume_ml')
    users = tuple(c.user for c in chunks)
    names = tuple(fmt(u) for u in users if u)

    if None in users:
      guest_trailer = ' (and possibly others)'
    else:
      guest_trailer = ''

    num = len(names)
    if num == 0:
      return 'no known drinkers'
    elif num == 1:
      ret = names[0]
    elif num == 2:
      ret = '%s and %s' % names
    elif num == 3:
      ret = '%s, %s and %s' % names
    else:
      if guest_trailer:
        return '%s, %s and at least %i others' % (names[0], names[1], num-2)
      else:
        return '%s, %s and %i others' % (names[0], names[1], num-2)

    return '%s%s' % (ret, guest_trailer)

  def GetTitle(self):
    return 'Session %i' % (self.seqn,)

  def Volume(self):
    return units.Quantity(self.volume_ml, units.RECORD_UNIT)

  def Duration(self):
    return self.endtime - self.startime

  def AddDrink(self, drink):
    super(DrinkingSession, self).AddDrink(drink)
    defaults = {'starttime': drink.starttime, 'endtime': drink.endtime}

    # Update or create a SessionChunk.
    chunk, created = SessionChunk.objects.get_or_create(session=self,
        user=drink.user, keg=drink.keg, defaults=defaults)
    chunk.AddDrink(drink)

    # Update or create a UserSessionChunk.
    chunk, created = UserSessionChunk.objects.get_or_create(session=self,
        user=drink.user, defaults=defaults)
    chunk.AddDrink(drink)

    # Update or create a KegSessionChunk.
    chunk, created = KegSessionChunk.objects.get_or_create(session=self,
        keg=drink.keg, defaults=defaults)
    chunk.AddDrink(drink)

  def UserChunksByVolume(self):
    chunks = self.user_chunks.all().order_by('-volume_ml')
    return chunks

  @classmethod
  def AssignSessionForDrink(cls, drink):
    # Return existing session if already assigned.
    if drink.session:
      return drink.session

    # Return last session if one already exists
    q = drink.site.sessions.all()
    window = datetime.timedelta(minutes=kb_common.DRINK_SESSION_TIME_MINUTES)
    session = find_object_in_window(q, drink.endtime, window)
    if session:
      session.AddDrink(drink)
      drink.session = session
      drink.save()
      return session

    # Create a new session
    session = cls(starttime=drink.starttime, endtime=drink.endtime,
        site=drink.site)
    session.save()
    session.AddDrink(drink)
    drink.session = session
    drink.save()
    return session

pre_save.connect(_set_seqn_pre_save, sender=DrinkingSession)


class SessionChunk(AbstractChunk):
  """A specific user and keg contribution to a session."""
  class Meta:
    unique_together = ('session', 'user', 'keg')
    get_latest_by = 'starttime'
    ordering = ('-starttime',)

  session = models.ForeignKey(DrinkingSession, related_name='chunks')
  user = models.ForeignKey(User, related_name='session_chunks', blank=True,
      null=True)
  keg = models.ForeignKey(Keg, related_name='session_chunks', blank=True,
      null=True)


class UserSessionChunk(AbstractChunk):
  """A specific user's contribution to a session (spans all kegs)."""
  class Meta:
    unique_together = ('session', 'user')
    get_latest_by = 'starttime'
    ordering = ('-starttime',)

  session = models.ForeignKey(DrinkingSession, related_name='user_chunks')
  user = models.ForeignKey(User, related_name='user_session_chunks', blank=True,
      null=True)


class KegSessionChunk(AbstractChunk):
  """A specific keg's contribution to a session (spans all users)."""
  class Meta:
    unique_together = ('session', 'keg')
    get_latest_by = 'starttime'
    ordering = ('-starttime',)

  objects = SessionManager()
  session = models.ForeignKey(DrinkingSession, related_name='keg_chunks')
  keg = models.ForeignKey(Keg, related_name='keg_session_chunks', blank=True,
      null=True)


class ThermoSensor(models.Model):
  class Meta:
    unique_together = ('site', 'seqn')

  site = models.ForeignKey(KegbotSite, related_name='thermosensors')
  seqn = models.PositiveIntegerField()
  raw_name = models.CharField(max_length=256)
  nice_name = models.CharField(max_length=128)

  def __str__(self):
    return self.nice_name

  def LastLog(self):
    try:
      return self.thermolog_set.latest()
    except Thermolog.DoesNotExist:
      return None

pre_save.connect(_set_seqn_pre_save, sender=ThermoSensor)


class Thermolog(models.Model):
  """ A log from an ITemperatureSensor device of periodic measurements. """
  class Meta:
    unique_together = ('site', 'seqn')
    get_latest_by = 'time'

  site = models.ForeignKey(KegbotSite, related_name='thermologs')
  seqn = models.PositiveIntegerField()
  sensor = models.ForeignKey(ThermoSensor)
  temp = models.FloatField()
  time = models.DateTimeField()

  def __str__(self):
    return '%s %.2f C / %.2f F [%s]' % (self.sensor, self.TempC(),
        self.TempF(), self.time)

  def TempC(self):
    return self.temp

  def TempF(self):
    return util.CtoF(self.temp)

  @classmethod
  def CompressLogs(cls):
    now = datetime.datetime.now()

    # keep at least the most recent 24 hours
    keep_time = now - datetime.timedelta(hours=24)

    # round down to the start of the day
    keep_date = datetime.datetime(year=keep_time.year, month=keep_time.month,
        day=keep_time.day)

    print "Compressing thermo logs prior to", keep_date

    def _LogGroup(sensor, records):
      num_readings = len(records)
      temps = [x.temp for x in records]
      min_temp = min(temps)
      max_temp = max(temps)
      sum_temps = sum(temps)
      mean_temp = sum_temps / num_readings

      base_date = records[0].time
      daily_date = datetime.datetime(year=base_date.year,
          month=base_date.month, day=base_date.day)

      print "%s\t%s\t%s\t%s\t%s" % (daily_date, num_readings, min_temp, max_temp,
          mean_temp)
      try:
        ThermoSummaryLog.objects.get(date=daily_date, period='daily')
        # Oops! Group already exists
        print "Warning: log already exists for", daily_date
        return
      except ThermoSummaryLog.DoesNotExist:
        pass
      new_rec = ThermoSummaryLog.objects.create(
          sensor=sensor,
          date=daily_date,
          period='daily',
          num_readings=num_readings,
          min_temp=min_temp,
          max_temp=max_temp,
          mean_temp=mean_temp)

    for sensor in ThermoSensor.objects.all():
      old_entries = sensor.thermolog_set.filter(time__lt=keep_date).order_by('time')

      group = []
      group_date = None
      for entry in old_entries:
        entry_date = datetime.datetime(year=entry.time.year,
            month=entry.time.month, day=entry.time.day)
        if group_date is None:
          group_date = entry_date
        if group_date == entry_date:
          group.append(entry)
        else:
          _LogGroup(sensor, group)
          group = [entry]
          group_date = entry_date

      if group:
        _LogGroup(sensor, group)

      old_entries.delete()

def thermolog_post_save(sender, instance, **kwargs):
  # TODO(mikey): prevent thermolog entries from being changed; if a particular
  # record is saved more than once, the average temperature will be invalid.
  daily_date = datetime.datetime(year=instance.time.year,
      month=instance.time.month,
      day=instance.time.day)
  defaults = {
      'site': instance.site,
      'num_readings': 1,
      'min_temp': instance.temp,
      'max_temp': instance.temp,
      'mean_temp': instance.temp,
  }
  daily_log, created = ThermoSummaryLog.objects.get_or_create(
      sensor=instance.sensor,
      period='daily',
      date=daily_date,
      defaults=defaults)

  if not created:
    new_mean = daily_log.num_readings * daily_log.mean_temp + instance.temp
    new_mean /= daily_log.num_readings + 1
    daily_log.mean_temp = new_mean

    daily_log.num_readings += 1

    if instance.temp > daily_log.max_temp:
      daily_log.max_temp = instance.temp
    if instance.temp < daily_log.min_temp:
      daily_log.min_temp = instance.temp

  daily_log.save()

pre_save.connect(_set_seqn_pre_save, sender=Thermolog)
post_save.connect(thermolog_post_save, sender=Thermolog)


class ThermoSummaryLog(models.Model):
  """A summarized temperature sensor log."""
  class Meta:
    unique_together = ('site', 'seqn')

  PERIOD_CHOICES = (
    ('daily', 'daily'),
  )
  site = models.ForeignKey(KegbotSite, related_name='thermosummarylogs')
  seqn = models.PositiveIntegerField()
  sensor = models.ForeignKey(ThermoSensor)
  date = models.DateTimeField()
  period = models.CharField(max_length=64, choices=PERIOD_CHOICES,
      default='daily')
  num_readings = models.PositiveIntegerField()
  min_temp = models.FloatField()
  max_temp = models.FloatField()
  mean_temp = models.FloatField()

pre_save.connect(_set_seqn_pre_save, sender=ThermoSummaryLog)


class RelayLog(models.Model):
  """ A log from an IRelay device of relay events/ """
  class Meta:
    unique_together = ('site', 'seqn')

  site = models.ForeignKey(KegbotSite, related_name='relaylogs')
  seqn = models.PositiveIntegerField()
  name = models.CharField(max_length=128)
  status = models.CharField(max_length=32)
  time = models.DateTimeField()

pre_save.connect(_set_seqn_pre_save, sender=RelayLog)


class Config(models.Model):
  def __str__(self):
    return '%s=%s' % (self.key, self.value)

  site = models.ForeignKey(KegbotSite, related_name='configs')
  key = models.CharField(max_length=255, unique=True)
  value = models.TextField()

  @classmethod
  def get(cls, key, default=None):
    try:
      return cls.objects.get(key=key)
    except cls.DoesNotExist:
      return default


class _StatsModel(models.Model):
  STATS_BUILDER = None
  class Meta:
    abstract = True
  site = models.ForeignKey(KegbotSite)
  date = models.DateTimeField(default=datetime.datetime.now)
  stats = fields.JSONField()
  revision = models.PositiveIntegerField(default=0)

  def Update(self, obj):
    builder = self.STATS_BUILDER()
    # TODO(mikey): use prev
    self.stats = builder.Build(obj)
    self.revision = builder.REVISION
    self.save()


class UserStats(_StatsModel):
  STATS_BUILDER = stats.DrinkerStatsBuilder
  user = models.ForeignKey(User, unique=True, related_name='stats')

  def __str__(self):
    return 'UserStats for %s' % self.user


class KegStats(_StatsModel):
  STATS_BUILDER = stats.KegStatsBuilder
  keg = models.ForeignKey(Keg, unique=True, related_name='stats')

  def __str__(self):
    return 'KegStats for %s' % self.keg


class SystemEvent(models.Model):
  class Meta:
    ordering = ('-when', '-id')
    get_latest_by = 'when'

  KINDS = (
      ('drink_poured', 'Drink poured'),
      ('session_started', 'Session started'),
      ('session_joined', 'User joined session'),
      ('keg_tapped', 'Keg tapped'),
      ('keg_ended', 'Keg ended'),
  )

  site = models.ForeignKey(KegbotSite)
  seqn = models.PositiveIntegerField()
  kind = models.CharField(max_length=255, choices=KINDS,
      help_text='Type of event.')
  when = models.DateTimeField(help_text='Time of the event.')
  user = models.ForeignKey(User, blank=True, null=True,
      related_name='events',
      help_text='User responsible for the event, if any.')
  drink = models.ForeignKey(Drink, blank=True, null=True,
      related_name='events',
      help_text='Drink involved in the event, if any.')
  keg = models.ForeignKey(Keg, blank=True, null=True,
      related_name='events',
      help_text='Keg involved in the event, if any.')
  session = models.ForeignKey(DrinkingSession, blank=True, null=True,
      related_name='events',
      help_text='Session involved in the event, if any.')

  @classmethod
  def ProcessDrink(cls, drink):
    keg = drink.keg
    site = drink.site
    if keg:
      q = keg.events.filter(kind='keg_started')
      if q.count() == 0:
        e = keg.events.create(site=site, kind='keg_started', when=drink.endtime,
            keg=keg)
        e.save()

    session = drink.session
    if session:
      q = session.events.filter(kind='session_started')
      if q.count() == 0:
        e = session.events.create(site=site, kind='session_started',
            when=session.starttime, user=drink.user)
        e.save()

    user = drink.user
    if user:
      q = user.events.filter(kind='session_joined')
      if q.count() == 0:
        e = user.events.create(site=site, kind='session_joined',
            when=drink.endtime, user=user)
        e.save()

    q = drink.events.filter(kind='drink_poured')
    if q.count() == 0:
      e = drink.events.create(site=site, kind='drink_poured',
          when=drink.endtime, drink=drink, user=drink.user, keg=drink.keg,
          session=drink.session)
      e.save()

pre_save.connect(_set_seqn_pre_save, sender=SystemEvent)
