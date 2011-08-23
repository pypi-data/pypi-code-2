# -*- coding: utf-8 -*-
#
# EquationOfTime is taken from Simon's Kennedy (python@sffjunkie.co.uk) astral.py - http://pypi.python.org/pypi/astral/0.5
#
# Copyright 2009-2011, Artiom MOLCHANOV ar.molchanov@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
from math import cos, sin, tan, acos, asin, atan2, floor, ceil, pi
from math import radians, degrees, pow
try:
    import pytz
except ImportError:
    #raise ImportError('The SolarTZ module requires the pytz module to be available.')
    #Without pytz we will suppose that all time values is in the UTC timezone.
    _PYTZ=False
else:
    _PYTZ=True

class SolarTZ(datetime.tzinfo):
    ZERO = datetime.timedelta(0)
    def __init__(self, longitude=0.0, eqtime=0):
        """
        :param longitude:  Longitude as a floating point number. Eastern longitudes should be negatives
        :type longitude:   float 
        :param eqtime:  Euqation of Time. 0 or 1 to select a built in equation or Euqation of Time function.
        :type longitude:   int or callable 
        """
        self._longitude=longitude
        self.__name='SolarTime(%.2f°)/UTC'%longitude
        if eqtime == 1:
            self.eq_of_time=self._eq_of_time1
        elif hasattr(eqtime, '__call__'):
            self.eq_of_time=eqtime
        else:
            self.eq_of_time=self._eq_of_time


    def utcoffset(self, dt):
        """
        Returns offset of Solar time from UTC, in minutes east of UTC. 
        If Solar time is west of UTC, this should be negative.
        :param dt:  Date and time in solar time
        :type dt:   datetime
        """
        if dt.tzinfo is not self:
            raise ValueError("%r is not Solar time"%dt.tzinfo) 
        date=dt.replace(tzinfo=None)
        offset=self.EquationOfTime(date)
        """
        offset must be a timedelta representing a whole number of minutes
        """
        mins=round(offset.total_seconds()/60.0)
        return datetime.timedelta(minutes=mins)
        
    def fromutc(self,dt):
        """
        :param dt:  UTC date and time
        :type dt:   datetime
        """
        if dt.tzinfo is self:
            date=dt.replace(tzinfo=None)
        else:
            date=dt
            dt.replace(tzinfo=self)
        offset=self.EquationOfTime(date)
        return dt+offset
        
    def solarnow(self):
        """
        Returns actual solar time on the choosen longitude. 
        """
        dt=datetime.datetime.utcnow()
        if _PYTZ:
            dt.replace(tzinfo=pytz.utc)
        return self.fromutc(dt)
        
    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return self.ZERO

    def EquationOfTime(self,dt=datetime.datetime.utcnow()):
        if dt.tzinfo is self: # Avoiding recursion
            raise ValueError("Can not use Solar Time here") 
        if dt.tzinfo is not None:
            zone = -dt.utcoffset().seconds / 3600.0
            if _PYTZ:
                utc_datetime = dt.astimezone(pytz.utc)
            else:
                utc_datetime = dt # Without pytz module we suppose that the time passed here is in UTC
        else:
            zone=0
            utc_datetime=dt
        timenow = utc_datetime.hour + (utc_datetime.minute / 60.0) + (utc_datetime.second / 3600)

        JD = self._julianday(utc_datetime.day, utc_datetime.month, utc_datetime.year)
        t = self._jday_to_jcentury(JD + timenow / 24.0)

        eqtime = self.eq_of_time(t)
    
        solarTimeFix = datetime.timedelta(minutes=(eqtime - (4.0 * self._longitude)+zone*60.))
        return solarTimeFix
        
    def _julianday(self, day, month, year):
        if month <= 2:
            year = year - 1
            month = month + 12
        
        A = floor(year / 100.0)
        B = 2 - A + floor(A / 4.0)

        jd = floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day - 1524.5
        if jd > 2299160.4999999:
            jd += B
            
        return jd
        
    def _jday_to_jcentury(self, julianday):
        return (julianday - 2451545.0) / 36525.0

    def _jcentury_to_jday(self, juliancentury):
        return (juliancentury * 36525.0) + 2451545.0

    def _mean_obliquity_of_ecliptic(self, juliancentury):
        seconds = 21.448 - juliancentury * (46.815 + juliancentury * (0.00059 - juliancentury * (0.001813)))
        return 23.0 + (26.0 + (seconds / 60.0)) / 60.0

    def _obliquity_correction(self, juliancentury):
        e0 = self._mean_obliquity_of_ecliptic(juliancentury)

        omega = 125.04 - 1934.136 * juliancentury
        return e0 + 0.00256 * cos(radians(omega))
    
    def _geom_mean_long_sun(self, juliancentury):
        l0 = 280.46646 + juliancentury * (36000.76983 + 0.0003032 * juliancentury)
        return l0 % 360.0
        
    def _eccentricity_earth_orbit(self, juliancentury):
        return 0.016708634 - juliancentury * (0.000042037 + 0.0000001267 * juliancentury)
        
    def _geom_mean_anomaly_sun(self, juliancentury):
        return 357.52911 + juliancentury * (35999.05029 - 0.0001537 * juliancentury)

    def _eq_of_time(self, juliancentury):
        epsilon = self._obliquity_correction(juliancentury)
        l0 = self._geom_mean_long_sun(juliancentury)
        e = self._eccentricity_earth_orbit(juliancentury)
        m = self._geom_mean_anomaly_sun(juliancentury)

        y = tan(radians(epsilon) / 2.0)
        y = y * y

        sin2l0 = sin(2.0 * radians(l0))
        sinm = sin(radians(m))
        cos2l0 = cos(2.0 * radians(l0))
        sin4l0 = sin(4.0 * radians(l0))
        sin2m = sin(2.0 * radians(m))

        Etime = y * sin2l0 - 2.0 * e * sinm + 4.0 * e * y * sinm * cos2l0 - \
                0.5 * y * y * sin4l0 - 1.25 * e * e * sin2m

        return degrees(Etime) * 4.0
##  Calculate the equation of time as per Carruthers et al.
    def _eq_of_time1(self, J_Day):
        #J_Day=self._jcentury_to_jday(juliancentury)
        t = (279.134 + 0.985647 * J_Day) * (pi/180.0)
    
        fEquation = 5.0323 - 100.976 * sin(t) + 595.275 * sin(2*t) + 3.6858 * sin(3*t) - 12.47 * sin(4*t) - 430.847 * cos(t) + 12.5024 * cos(2*t) + 18.25 * cos(3*t)
    
        #Convert seconds to hours.
        fEquation = fEquation / 3600.00

        return fEquation                    
