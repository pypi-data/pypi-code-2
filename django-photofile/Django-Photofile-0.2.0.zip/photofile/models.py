#coding=utf-8
import os
from photofile import get_filename, generate_thumb
from django.db import models
from metadata import get_metadata

class PhotoMetadata(models.Model):

    class Meta:
        abstract = True

    metadata_processed = models.NullBooleanField(default = False, null = True, blank = True)

    width = models.IntegerField(default = 0, null = True, blank = True)
    height = models.IntegerField(default = 0, null = True, blank = True)

    longitude = models.FloatField(null = True, blank = True)
    latitude = models.FloatField(null = True, blank = True)
    altitude = models.FloatField(null = True, blank = True)

    exif_date = models.DateTimeField(null = True, blank = True)
    camera_model = models.CharField(max_length = 50, blank = True, null = True)
    orientation = models.IntegerField(blank = True, null = True)
    exposure_time = models.FloatField(blank = True, null = True)
    fnumber = models.FloatField(blank = True, null = True)
    exposure_program = models.IntegerField(blank = True, null = True)
    iso_speed = models.IntegerField(blank = True, null = True)
    metering_mode = models.IntegerField(blank = True, null = True)
    light_source = models.IntegerField(blank = True, null = True)
    flash_used = models.IntegerField(blank = True, null = True)
    focal_length = models.FloatField(max_length = 50, blank = True, null = True)
    exposure_mode = models.IntegerField(blank = True, null = True)
    whitebalance = models.IntegerField(blank = True, null = True)
    focal_length_in_35mm = models.CharField(max_length = 50, blank = True, null = True)

    def populate_metadata(self, do_save=True):
        filename = get_filename(self)
        data = get_metadata(filename)
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.metadata_processed = True

    def save(self, force_insert=False, force_update=False):
        super(PhotoMetadata, self).save(force_insert, force_update)
        if not self.metadata_processed:
            self.populate_metadata()
            super(PhotoMetadata, self).save(force_insert, force_update)

    def thumbnail_url(self):
        complete_filename = get_filename(self)
        return '<img src="%s"/>' % generate_thumb(complete_filename, 100, 100, True)
    thumbnail_url.allow_tags = True
    thumbnail_url.short_description ="Photo"

