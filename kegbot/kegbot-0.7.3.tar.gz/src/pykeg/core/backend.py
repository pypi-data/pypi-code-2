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

"""Wrapper module for database implementation."""

import datetime
import logging

from django.db.utils import DatabaseError

from pykeg.core import kb_common
from pykeg.core import config
from pykeg.core import models
from pykeg.core import protolib

class BackendError(Exception):
  """Base backend error exception."""

class Backend:
  """Abstract base Kegbot backend class.

  This class defines the interface that pykeg uses to talk to the kegbot
  backend.
  """

  def GetConfig(self):
    """Returns a KegbotConfig instance based on the current database values."""
    raise NotImplementedError

  def GetUserFromUsername(self, username):
    """Returns the User matching the given username, or None."""
    raise NotImplementedError

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    """Creates a new User instance.

    Args
      username: the unique username for the new User
      gender: the gender to assign the new user
      weight: the weight to assign the new user
    Returns
      the new User instance
    """
    raise NotImplementedError

  def GetAllTaps(self):
    """Returns all currently enabled taps."""
    raise NotImplementedError

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=None, auth_token=None):
    """Records a new drink with the given parameters."""
    raise NotImplementedError

  def LogSensorReading(self, sensor_name, temperature, when):
    """Records a new sensor reading."""
    raise NotImplementedError

  def GetAuthToken(self, auth_device, token_value):
    """Returns an AuthenticationToken instance."""
    raise NotImplementedError


class KegbotBackend(Backend):
  """Django models backed Backend."""

  def __init__(self):
    self._logger = logging.getLogger('backend')
    self._config = config.KegbotConfig(self._GetConfigDict())

  def _GetConfigDict(self):
    try:
      ret = {}
      for row in models.Config.objects.all():
        ret[row.key] = row.value
      return ret
    except DatabaseError, e:
      raise BackendError, e

  def _GetTapFromName(self, tap_name):
    try:
      return models.KegTap.objects.get(meter_name=tap_name)
    except models.KegTap.DoesNotExist:
      return None

  def _GetKegForTapName(self, tap_name):
    tap = self._GetTapFromName(tap_name)
    if tap and tap.current_keg and tap.current_keg.status == 'online':
      return tap.current_keg
    return None

  def _GetSensorFromName(self, name, autocreate=True):
    try:
      return models.ThermoSensor.objects.get(raw_name=name)
    except models.ThermoSensor.DoesNotExist:
      if autocreate:
        sensor = models.ThermoSensor(raw_name=name, nice_name=name)
        sensor.save()
        return sensor
      else:
        return None

  def _GetUserObjFromUsername(self, username):
    try:
      return models.User.objects.get(username=username)
    except models.User.DoesNotExist:
      return None

  def GetConfig(self):
    return self._config

  def GetUserFromUsername(self, username):
    return protolib.ToProto(self._GetUserObjFromUsername(username))

  def CreateNewUser(self, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    u = models.User(username=username)
    u.save()
    p = u.get_profile()
    p.gender = gender
    p.weight = weight
    p.save()
    return protolib.ToProto(u)

  def CreateAuthToken(self, auth_device, token_value, username=None):
    token = models.AuthenticationToken.objects.create(
        auth_device=auth_device, token_value=token_value)
    if username:
      user = self._GetUserObjFromUsername(username)
      token.user = user
    token.save()
    return protolib.ToProto(token)

  def GetAllTaps(self):
    return protolib.ToProto(list(models.KegTap.objects.all()))

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=None, auth_token=None):

    tap = self._GetTapFromName(tap_name)

    d = models.Drink(ticks=ticks)

    if volume_ml is not None:
      d.volume_ml = volume_ml
    else:
      d.volume_ml = float(ticks) * tap.ml_per_tick

    if username:
      d.user = self._GetUserObjFromUsername(username)

    if not pour_time:
      pour_time = datetime.datetime.now()
    d.endtime = pour_time

    if duration:
      d.starttime = pour_time - datetime.timedelta(seconds=duration)
      d.duration = duration
    else:
      d.starttime = pour_time
      d.duration = 0

    # Look up the current keg.
    if tap.current_keg and tap.current_keg.status == 'online':
      d.keg = tap.current_keg

    d.auth_token = auth_token
    models.DrinkingSession.AssignSessionForDrink(d)
    d.save()

    d.PostProcess()

    return protolib.ToProto(d, full=False)

  def LogSensorReading(self, sensor_name, temperature, when):
    sensor = self._GetSensorFromName(sensor_name)
    res = models.Thermolog.objects.create(sensor=sensor, temp=temperature,
        time=when)
    res.save()
    return protolib.ToProto(res, full=False)

  def GetAuthToken(self, auth_device, token_value):
    try:
      return protolib.ToProto(models.AuthenticationToken.objects.get(
          auth_device=auth_device, token_value=token_value))
    except models.AuthenticationToken.DoesNotExist:
      return None
