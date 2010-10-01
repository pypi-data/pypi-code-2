# -*- coding: utf-8 -*-

"""Github

This plugin currently doesn't support the Github`s timezone information.
"""

from datetime import datetime, timedelta
import re
import urllib2

from django.utils import simplejson

from issues.core import TrackerPlugin
from issues.models import Issue, IssueUser, UserMapping
from issues.signals import post_tracker_sync, post_issue_sync

CONFIG_PATTERN = re.compile(r"""^(?P<user>\S+)@(?P<project>\S+)$""")

GITHUB_TIMEZONE = '-0700'
GITHUB_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'


def _github_date_to_datetime(value):
    date_without_tz = ' '.join(value.strip().split()[:2])
    return datetime.strptime(date_without_tz, GITHUB_DATE_FORMAT)


class Github(TrackerPlugin):

    id = 'github'
    name = 'Github issue synchronisation'
    api_url = 'http://github.com/api/v2/json/issues'

    def _make_request(self, url):
        req = urllib2.Request(url)
        fo = urllib2.urlopen(req)
        response = fo.read()
        response = simplejson.loads(response)
        fo.close()
        return response

    def _update_user_data(self, config, data, issue):
        names = [data.get('user')]
        url = '%(base_url)s/comments/%(user)s/%(project)s/%(issue)s' % {
            'base_url': self.api_url,
            'user': config.get('user'),
            'project': config.get('project'),
            'issue': issue.no}
        response = self._make_request(url)
        for comment in response.get('comments', []):
            names.append(comment.get('user'))
        names = list(set(names))
        self.update_user_mapping(issue, names)

    def sync(self, tracker):
        m = CONFIG_PATTERN.match(tracker.config)
        if not m:
            raise StandardError('Invalid configuration information.'
                                ' Please use a format like user@project.')
        config = m.groupdict()
        response = {}
        url = '%(base_url)s/list/%(user)s/%(project)s/%%s' % {
            'base_url': self.api_url,
            'user': config.get('user'),
            'project': config.get('project')}
        try:
            response_closed = self._make_request(url % 'closed')
            response_open = self._make_request(url % 'open')
        except urllib2.HTTPError, e:
            self._log.error(str(e))
            return False
        issues = response_closed.get('issues', [])
        issues.extend(response_open.get('issues'))
        for data in issues:
            tid = data.get('number')
            created = _github_date_to_datetime(data.get('created_at'))
            updated = _github_date_to_datetime(data.get('updated_at'))
            if (created >= tracker.last_update
                or updated >= tracker.last_update):
                issue = Issue.by_tracker_id(tracker.id, tid)
                issue.no = tid
                issue.set_title(data.get('title', ''))
                issue.set_description(data.get('body', ''))
                issue.tracker = tracker
                issue.last_change = updated
                issue.owner = data.get('user')
                issue.reporter = data.get('user')
                if data.get('closed_at', None):
                    issue.active = False
                else:
                    issue.active = True
                if not issue.id:
                    issue.created = datetime.now()
                issue.updated = datetime.now()
                issue.save()
                post_issue_sync.send(sender=self, issue=issue)
                # Currently disabled due to API call limitations
                #self._update_user_data(config, data, issue)
            else:
                continue
        tracker.last_update = datetime.now() - timedelta(days=1)
        tracker.save()
        post_tracker_sync.send(sender=self, tracker=tracker)
        return True
