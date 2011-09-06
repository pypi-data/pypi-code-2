"""This file provides the fetching and converting of the
feed from delicious.com.
"""

from causal.main.handlers import BaseServiceHandler
from causal.main.models import ServiceItem
from causal.main.exceptions import LoggedServiceError
from causal.main.utils.services import get_url
from django.shortcuts import render_to_response, redirect
from dateutil import parser
from datetime import datetime, timedelta
from django.utils import simplejson

class ServiceHandler(BaseServiceHandler):
    display_name = 'Delicious'

    def get_items(self, since):
        """Get data too display for main page."""
        url = 'http://feeds.delicious.com/v2/json/%s?count=100' % (
            self.service.auth.username,
        )

        user_feed = get_url(url)
        if user_feed:
            return self._convert_feed(user_feed, since)

    def get_stats_items(self, since):
        """Stubbed out for now"""
        return self.get_items(since)
    
    def _convert_feed(self, json, since):
        """Convert the json feed into Service Items limiting on since.
        """

        items = []

        for entry in json:
            # Check we have a valid feed
            if entry.has_key('d') and entry['d'] != '404 Not Found':
                item = ServiceItem()
                created = datetime.strptime(entry['dt'], '%Y-%m-%dT%H:%M:%SZ') #'2010-11-23T22:03:29Z'
                if created.date() >= since:
                    try:
                        item.title = entry['d']
                        item.body = entry['n']
                        item.created = created
                        item.link_back = entry['u']
                        item.notes = entry['n']
                        item.tags = entry['t']
                        item.service = self.service
                        items.append(item)
                    except:
                        pass

        return items
