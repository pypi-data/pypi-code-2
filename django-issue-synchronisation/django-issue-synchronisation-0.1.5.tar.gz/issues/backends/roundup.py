# -*- coding: utf-8 -*-

"""Roundup XML-RPC interface

TODO: Descriptions are not necessary for Roundup, currently the backend always
      takes the first message attachted to the issue. That doesn't have to be
      the issue`s real description, but there is no other rule for getting this
      information.
"""

import time

from datetime import datetime, timedelta
from xmlrpclib import DateTime, ServerProxy

from issues.core import TrackerPlugin
from issues.models import Issue, IssueUser, Tracker, UserMapping
from issues.signals import post_tracker_sync, post_issue_sync


ROUNDUP_DATE_FORMAT = '<Date %Y-%m-%d.%H:%M:%S.%f>'

STATUS_UNREAD = 1
STATUS_RESET = 2
STATUS_FOR_DISCUSSION = 3
STATUS_EXAMPLE_NEEDED = 4
STATUS_WORK_IN_PROGRESS = 5
STATUS_TESTING = 6
STATUS_DONE_PROVISIONALLY = 7
STATUS_DONE = 8

ACTIVE_STATUS = (STATUS_UNREAD,
                 STATUS_RESET,
                 STATUS_FOR_DISCUSSION,
                 STATUS_EXAMPLE_NEEDED,
                 STATUS_WORK_IN_PROGRESS,
                 STATUS_TESTING)


def _roundup_date_to_datetime(value):
    """Converts a Roundup date string to datetime object.

    :param value: A datetime string
    :returns: :class:`datetime.datetime`
    """
    return datetime.strptime(value, ROUNDUP_DATE_FORMAT)


class Roundup(TrackerPlugin):

    id = 'roundup'
    name = 'Roundup XML-RPC issue synchronisation'

    def _get_users(self, server):
        """Return a userid/username dictionary.

        :param server: :class:`ServerProxy`
        :returns: Dictionary, containing userid,username key value pairs
        """
        retval = {}
        ids = map(int, server.list('user', 'id'))
        for user_id in ids:
            data = server.display('user%d' % user_id)
            retval[user_id] = data['username']
        return retval

    def _get_description(self, server, message_list):
        """Get an issue`s description.

        :param server: :class:`ServerProxy`
        :param issue_id: An issue`s id
        :returns: Empty string or the issue`s description
        """
        if len(message_list) == 0:
            return ''
        messages = map(int, message_list)
        messages.sort()
        msg_id, = messages[:1]
        data = server.display('msg%d' % msg_id)
        return data.get('summary', '')

    def _update_user_data(self, server, data, issue, users):
        """Updates the affected user per issue.

        :param server: :class:`ServerProxy`
        :param data: Data dictionary
        :param issue: :class:`Issue`
        :param users: User dictionary
        """
        names = [users[int(data['creator'])]]
        owner = users[int(data.get('assignedto'))]
        if not owner in names:
            names.append(owner)
        messages = map(int, data.get('messages', []))
        for msg_id in messages:
            data = server.display('msg%d' % msg_id)
            author = users.get(int(data['author']), None)
            if author is not None and author not in names:
                names.append(author)
        names = list(set(names))
        self.update_user_mapping(issue, names)

    def sync(self, tracker):
        server = ServerProxy(tracker.config, allow_none=True,
                             use_datetime=datetime)
        last_update = DateTime(time.mktime(tracker.last_update.timetuple()))
        users = self._get_users(server)
        ids = map(int, server.filter('issue', None, {'activity':
                                                     str(last_update)}))
        for issue_id in ids:
            data = server.display('issue%d' % issue_id, 'title', 'creation',
                                  'creator', 'assignedto', 'activity',
                                  'messages', 'status')
            issue = Issue.by_tracker_id(tracker.id, issue_id)
            issue.no = issue_id
            issue.set_title(data.get('title', ''))
            issue.set_description(self._get_description(
                server, data.get('messages', [])))
            issue.reporter = users[int(data['creator'])]
            issue.owner = users[int(data['assignedto'])]
            issue.last_change = _roundup_date_to_datetime(data.get('activity'))
            status = int(data.get('status', -1))
            issue.active = status in ACTIVE_STATUS
            issue.tracker = tracker
            if not issue.id:
                issue.created = datetime.now()
            issue.updated = datetime.now()
            issue.save()
            post_issue_sync.send(sender=self, issue=issue)
            self._update_user_data(server, data, issue, users)
        tracker.last_update = datetime.now() - timedelta(days=1)
        tracker.save()
        post_tracker_sync.send(sender=self, tracker=tracker)
        return True
