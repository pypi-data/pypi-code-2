# -*- coding: utf-8 -*-

"""A sample hook implementation."""

from issues.signals import post_tracker_sync


def print_tracker(tracker, **kwargs):
    print str(tracker)

post_tracker_sync.connect(print_tracker)