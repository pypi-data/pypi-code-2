# -*- coding: utf-8 -*-

import logging

from issues.models import IssueUser, UserMapping
from issues.plugin import Plugin


class TrackerPlugin(Plugin):

    def __init__(self):
        self._log = logging.getLogger("%s.%s" % (__name__,
                                                 self.__class__.__name__))

    def load(self):
        """A plugin`s load event."""
        self._log.debug("Loading")

    def sync(self, tracker):
        """Start the synchronisation process for a single tracker.

        :param tracker: Instance of :class:`System`
        """
        raise NotImplementedError

    def unload(self):
        """A plugin`s unload event."""
        self._log.debug("Unloading")

    def update_user_mapping(self, issue, names):
        """Updates the list of affected user per issue.

        :param issue: :class:`Issue`
        :param names: A list of string names
        """
        if not names:
            return
        query = IssueUser.objects.filter(issue=issue)
        query.delete()
        for name in names:
            user_mapping = UserMapping.objects.filter(
                tracker=issue.tracker, login_name=name)
            if user_mapping.count() != 0:
                user_mapping = user_mapping[0]
                issue_user = IssueUser.objects.filter(issue=issue,
                                                      user=user_mapping.user)
                if issue_user.count() == 0:
                    iu = IssueUser()
                    iu.user = user_mapping.user
                    iu.issue = issue
                    iu.save()
            else:
                self._log.warning('Missing user mapping entry for user "%s"'
                                  ' and issue #%d (%s)'
                                  % (name, issue.no, issue.tracker))
