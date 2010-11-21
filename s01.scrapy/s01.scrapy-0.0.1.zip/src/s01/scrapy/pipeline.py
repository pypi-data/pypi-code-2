###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Scrapy pipeline for xspider.foo project

"""

import csv

import scrapy.exceptions
import scrapy.contrib.exporter
from scrapy.conf import settings
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

import s01.scrapy.util


class TestItemExporter(scrapy.contrib.exporter.BaseItemExporter):
    """Item exporter for TestExportPipeline"""

    def __init__(self, file):
        self.export_empty_fields = False
        self.include_headers_line = True
        self.encoding = 'utf-8'
        self.writer = csv.writer(file)
        self._headers_not_written = True

    def _ensureHeaders(self, item):
        if self._headers_not_written:
            self._headers_not_written = False
            self.fields_to_export = item.fields.keys()
            self.writer.writerow(self.fields_to_export)

    def export_item(self, item):
        self._ensureHeaders(item)
        fields = self._get_serialized_fields(item, default_value='',
            include_empty=True)
        values = [field[1] for field in fields]
        self.writer.writerow(values)


class TestExportPipeline(object):
    """Scrapy test export pipeline"""

    def __init__(self):
        tmpDirPath = settings.get('S01_SCRAPY_TEST_EXPORT_DIR')
        if not tmpDirPath:
            raise scrapy.exceptions.NotConfigured
        fName = s01.scrapy.util.getNewFileName(tmpDirPath)
        self.file = open(fName, 'wb')
        self.exporter = TestItemExporter(self.file)
        self.exporter.start_exporting()
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def engine_stopped(self):
        self.exporter.finish_exporting()
        self.file.close()
