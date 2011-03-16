# -*- coding: utf-8 -*-

"""Trac XML-RPC interface"""

from datetime import datetime, timedelta
import socket
import sys
import time
from xmlrpclib import DateTime, ServerProxy, ProtocolError, Error

from issues.core import TrackerPlugin
from issues.models import Issue, IssueUser, Tracker, UserMapping
from issues.signals import post_tracker_sync, post_issue_sync


class Trac(TrackerPlugin):

    id = 'trac'
    name = 'Trac XML-RPC issue synchronisation'

    def _update_user_data(self, server, data, issue):
        """Update user specific data.

        :param server: :class:`ServerProxy` instance
        :param data: A data dictionary result from `ticket.get`
        :param issue: :class:`Issue` instance
        """
        names = [data.get('owner')]
        reporter = data.get('reporter')
        if not reporter in names:
            names.append(reporter)
        if (isinstance(data.get('cc', None), basestring)
            and len(data.get('cc')) > 0):
            for item in data.get('cc').split(','):
                if item and not item in names:
                    names.append(item.strip())
        for item in server.ticket.changeLog(issue.no):
            author = item[1]
            if author and not author in names:
                names.append(author)
        names = list(set(names))
        self.update_user_mapping(issue, names)

    def sync(self, tracker):
        api_version = [0]
        server = ServerProxy(tracker.config, allow_none=False,
                             use_datetime=datetime)
        try:
            api_version = server.system.getAPIVersion()
        except socket.gaierror, err:
            self._log.error('Network error: %s', err)
            return False
        except ProtocolError, err:
            self._log.error('Protocol error: %s %s' % (
                err.errcode, err.errmsg))
            return False
        except Error, err:
            self._log.error('Error: %s' % err)
            return False
        except:
            self._log.error('Unknown error: %s' % str(sys.exc_info()[1]))
            return False
        self._log.info('Trac XMLRPC-API version: %s' % '.'.join(map(
            str, api_version)))
        d = DateTime(time.mktime(tracker.last_update.timetuple()))
        self._log.info('Last update: %s' % d)
        tids = server.ticket.getRecentChanges(d)
        self._log.info('Issue updates: %s' % `tids`)
        for tid in tids:
            issue = Issue.by_tracker_id(tracker.id, tid)
            id_, cr_date, last_change, data = server.ticket.get(tid)
            #if isinstance(cr_date, int):
                #cr_date = datetime.fromtimestamp(cr_date)
                #last_change = datetime.fromtimestamp(last_change)
            issue.no = id_
            issue.set_title(data.get('summary', ''))
            issue.set_description(data.get('description', ''))
            issue.reporter = data.get('reporter')
            issue.owner = data.get('owner')
            issue.last_change = last_change
            issue.tracker = tracker
            # issue.active can't be resolved, as Trac allows renaming
            # of status values.
            if not issue.id:
                issue.created = datetime.now()
            issue.updated = datetime.now()
            issue.save()
            post_issue_sync.send(sender=self, issue=issue)
            self._update_user_data(server, data, issue)
        tracker.last_update = datetime.now() - timedelta(days=1)
        tracker.save()
        post_tracker_sync.send(sender=self, tracker=tracker)
        return True
