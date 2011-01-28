# -*- coding: utf-8 -*-

from plone.app.blob.migrations import migrate

def migrateImagedEvent(context):
    return migrate(context, "Event", meta_type="ATEvent")
