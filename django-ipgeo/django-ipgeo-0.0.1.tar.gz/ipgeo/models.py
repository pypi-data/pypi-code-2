# -*- coding: utf-8 -*-
import socket
import struct

from django.db import models
from django.core.urlresolvers import reverse

class Location(models.Model):
    name = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=10, decimal_places=6)
    lon = models.DecimalField(max_digits=10, decimal_places=6)

    def __unicode__(self):
        return self.name


class RangeManager(models.Manager):
    def find(self, ip):
        """
        Find the smallest range contains the given IP
        """

        number = struct.unpack('!L', socket.inet_aton(ip))[0]
        ranges = self.get_query_set()\
                     .filter(start__lte=number, end__gte=number)\
                     .order_by('end', '-start')\
                     .select_related()
        print 'Ranges:'
        for rang in ranges:
            print rang.country, rang.location
        try:
            return ranges[0]
        except IndexError:
            raise Range.DoesNotExist()


class Range(models.Model):
    start = models.BigIntegerField(max_length=50, db_index=True)
    end = models.BigIntegerField(max_length=50, db_index=True)
    country = models.CharField(max_length=2)
    description = models.CharField(max_length=33)
    location = models.ForeignKey('ipgeo.Location', null=True)

    def __unicode__(self):
        return self.description

    objects = RangeManager()
