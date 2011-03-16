# -*- coding: utf-8 -*-

"""Custom signals used during the sync process."""

from django.dispatch import Signal

post_tracker_sync = Signal(providing_args=['tracker'])
post_issue_sync = Signal(providing_args=['issue'])