import dm.environment
import mx.DateTime
import time

# Unixtime max value: January 19, 2038 03:14:07 GMT

# To adjust the system time and timezone:
#  - use `ntpdate' to set host time (/etc/init.d/ntpdate restart).
#  - use `tzconfig' to set host timezone (/usr/sbin/tzconfig).
#
# This module was written to fix unidentified localtime()
# problems when runing Python in Apache on Debian.

# Todo: Fix up for conversion between universal and localtime when 
# converted time is in opposite daylight saving state from localtime()

# todo: Clean up all this. It was just a Django setting error la la la.

def getLocalNow():
    return convertUniversalToLocal(getUniversalNow())

def getLocalNowC():
    return convertDateTimeToC(getLocalNow())

def getLocalNowCWithZone():
    localNow = getLocalNow()
    return convertDateTimeToC(localNow) +" "+ getLocalZoneName(localNow.ticks())

def getUniversalNow():
    return mx.DateTime.utc()

def convertDateTimeToC(dateTime):
    return mx.DateTime.ctime(dateTime)

def convertUniversalToLocal(utcTime):
    return utcTime - getDiffLocalToUniversal(utcTime.ticks())

def convertLocalToUniversal(localTime):
    return localTime + getDiffLocalToUniversal(localTime.ticks())

def getDiffLocalToUniversal(refSeconds):
    if isDaylightSavingTime(refSeconds):
        seconds = time.altzone
    else:
        seconds = time.timezone
    return mx.DateTime.DateTimeDeltaFromSeconds(seconds)

def isDaylightSavingTime(refSeconds):
    return (time.localtime(refSeconds)[-1] > 0)

def getLocalZoneName(refSeconds):
    if isDaylightSavingTime(refSeconds):
        return time.tzname[1]
    else:
        return time.tzname[0]

def resetTimezone():
    time.tzset()

