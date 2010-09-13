# -*- coding: utf-8 -*-

"""Trac database interface

Synchronises issue changes via a direct database connection.

TODO:
  * Currently doesn't support schema names
"""

from datetime import datetime, timedelta
import time

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from issues.core import TrackerPlugin
from issues.models import Issue, IssueUser, Tracker, UserMapping
from issues.signals import post_tracker_sync, post_issue_sync


_engine = None
metadata = None
session = None

class Trac(TrackerPlugin):

    id = 'trac_db'
    name = 'Trac direct-db synchronisation'

    def _connect(self, tracker):
        """Creates a database session and the metadata.

        :param tracker: :class:`Tracker`
        """
        global _engine, metadata, session
        _engine = create_engine(tracker.config)
        Session = sessionmaker()
        Session.configure(bind=_engine)
        session = Session()
        metadata = MetaData(_engine)
        metadata.reflect()

    def _update_user_data(self, server, data, issue):
        """Update user specific data.

        :param server: :class:`ServerProxy` instance
        :param data: :class:`Table` instance from SQLAlchemy
        :param issue: :class:`Issue` instance
        """
        pass

    def sync(self, tracker):
        global metadata
        try:
            self._connect(tracker)
        except DBAPIError, err:
            self._log.error('DB API error: %s', err)
            return False
        except:
            self._log.error('Unknown error: %s' % str(sys.exc_info()[1]))
            return False
        #Ticket = metadata.tables['ticket']
        last_update = time.mktime(tracker.last_update.timetuple())
        self._log.info('Last update: %s' % last_update)
        Ticket = Table('ticket', metadata, schema='avsweb', autoload=True)
        query = session.query(Ticket)
        query = query.filter('time >= :time')
        query = query.params(time=last_update)
        for i in query:
            issue = Issue.by_tracker_id(tracker.id, i.id)
            issue.no = i.id
            issue.title = i.summary[:255]
            issue.description = i.description[:5000]
            issue.reporter = i.reporter
            issue.owner = i.owner
            issue.last_change = datetime.fromtimestamp(i.changetime)
            if issue.active == None:
                issue.active = True
            issue.tracker = tracker
            issue.save()
            post_issue_sync.send(sender=self, issue=issue)
        tracker.last_update = datetime.now() - timedelta(days=1)
        tracker.save()
        post_tracker_sync.send(sender=self, tracker=tracker)
