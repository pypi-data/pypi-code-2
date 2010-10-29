# -*- coding: utf-8 -*-
# (c) 2008-2009, Marcin Kasperski

import twisted.web.client as webclient
from twisted.internet import defer, reactor
import logging
import base64
import datetime

log = logging.getLogger("mekk.nozbe")

class NozbeLegacyApi(object):
    """
    Wrapper for old, documented Nozbe API (http://www.nozbe.com/gtd/api).
    At the moment only querying functions are implemented
    """
    api_url = "api"

    def __init__(self, nozbe_connection):
        self.connection = nozbe_connection

    def get_projects(self):
        return self.connection.get_request(self.api_url, "projects")
    def get_contexts(self):
        return self.connection.get_request(self.api_url, "contexts")
    def get_project_actions(self, project_id):
        return self.connection.get_request(
            self.api_url, "actions", "what-project", id = project_id)

class NozbeSyncApi(object):
    """
    Wrapper for newer, not officially documented Nozbe "Sync" API
    (the API which is claimed to be used for iPhone application sync).

    get_* methods read data, returning list of dictionaries (as deferreds)

    add_*, delete_* and update_* methods register modifications to
    be executed, but do not execute them. All those functions return
    identifier assigned to new item by the library (which will be
    present as 'id' in legacy API).

    save_changes method actually saves to Nozbe all the changes
    previously saved using add_*, deletel_* and update_* (and returns
    deferred fired once the changes are actually saved)

    It is recommended to bundle many changes together and then save
    them as it puts less stress on the server than individually saving
    every change.
    """

    api_url = "sync"
    app_id = "997"

    RECUR_NO_REPEAT = 0
    RECUR_EVERY_DAY = 1
    RECUR_EVERY_WEEKDAY = 2
    RECUR_EVERY_WEEK = 3
    RECUR_EVERY_TWO_WEEKS = 4
    RECUR_EVERY_MONTH = 5
    RECUR_EVERY_HALF_A_YEAR = 6
    RECUR_EVERY_YEAR = 7

    # Use NozbeApi.recur_label(code) instead of checking this directly
    recur_labels = {
        '0' : u"No",
        '1' : u"Every day",
        '2' : u"Every weekday",
        '3' : u"Every week",
        '4' : u"Every two weeks",
        '5' : u"Every month",
        '6' : u"Every half a year",
        '7' : u"Every year",
    }

    def __init__(self, nozbe_connection):
        self.connection = nozbe_connection
        self._reset_pending_updates()
        self._update_id = 1

    def get_projects(self):
        """
        Returns the project list. Every project is a dictionary containing:
        - hash (nozbe project identifier),
        - name (short name),
        - body (description),
        - tag (space separated tag list),
        - count (unfinished actions count),
        - share (co-owners - as list of name,hash dictionaries)
        - ts (timestamp - looks like datetime of last project change but I am not sure)
        """
        return self._get_data("project")
    def get_contexts(self):
        """
        Returns the context list. Every context is a dictionary containing:
        - hash (context identifier),
        - name (short name),
        - body (description),
        - icon (icon identifier),
        - count (unfinished actions count),
        - ts (timestamp)
        """
        return self._get_data("context")
    def get_tasks(self):
        """
        Returns the unfinished task list. Every task is a dictionary containing:
        - hash (task identifier),
        - name (short name),
        - name_show, (short name with textile markup applied)
        - date     (date finished)
        - datetime (due date)
        - recur    (see constants RECUR_ above)
        - time     (estimated work cost - in minutes)
        - context_hash ('hash' of (first) context the task belongs to)
        - context_id   (legacy id of the same context - should match LegacyAPI)
        - project_hash ('hash' of the project the task belongs to)
        - project_id   (legacy id of the same project)
        - next     (1 - it is "next action", 0 - it is not)
        - re_user  (0 if I am responsible, otherwise hash of the person the task is delegated to)
        - ts  (task timestamp)

        The names date, datetime and time are confusing and
        unfortunate, but after some hesitation I decided not to change
        them, they are called so in the Nozbe API itself.
        """
        return self._get_data("task")
    def get_completed_tasks(self):
        """
        Just like get_tasks but returns finished tasks
        """
        return self._get_data("task", showdone = "1")
    def get_notes(self):
        """
        Returns the note list. Every item is a dictionary with:
        - hash (id of a note)
        - name (note title)
        - body (note text)
        - body_show (note text with textile markup applied)
        - date (?)
        - context_hash  (just like for task)
        - context_id
        - project_hash
        - project_id
        - ts  (timestamp)
        """
        return self._get_data("note")
    def get_uploads(self):
        """
        Returns the upload list. Every item contains:
        - hash,
        - name,
        - date,
        - size (in bytes)
        - context_id
        - context_hash
        - project_id
        - project_hash
        - ts
        """
        return self._get_data("upload")
    def get_all(self):
        """
        Returns everything: projects, contexts, tasks, notes and
        uploads - together.

        Returned item is a dictionary contaning:
        - project => project list (as returned by get_projects)
        - context => context list (as returned by get_contexts)
        - task => task list (as returned by get_tasks)
        - note => notes list (as returned by get_notes)
        - upload => upload list (as returned by get_uploads)

        It is (claimed to be) a bit faster than grabbing every item
        separately.
        """
        return self.connection.get_request(self.api_url, "getdata", dev=self.app_id, what="all")
    def get_ts(self):
        """
        Returns timestamps for all data types (information when those data
        were changed). Returns a dictionary mapping data type (keys like in get_all) to timestamp.
        """
        return self.connection.get_request(self.api_url, "getts")

    ### Funkcje modyfikujące. Zwracają id dodane do rekordu

    def add_project(self, name, body = "", tag = ""):
        return self._add_record('project',
                                dict(name = name, body = body, tag = tag))

    def update_project(self, record):
        return self._update_record('project', record.copy())

    def delete_project(self, record):
        return self._delete_record('project', record.copy())

    def add_context(self, name, body = "", icon = ""):
        return self._add_record('context',
                                dict(name = name, body = body, icon = icon))

    def update_context(self, record):
        return self._update_record('context', record.copy())

    def delete_context(self, record):
        return self._delete_record('context', record.copy())

    def add_tag(self, name):
        return self._add_record('tag',
                                dict(name = name))

    def update_tag(self, record):
        return self._update_record('tag', record.copy())

    def delete_tag(self, record):
        return self._delete_record('tag', record.copy())

    def add_task(self, name, project_hash, context_hash = "",
                 date = "", datetime = "", recur = 0, # NozbeSyncApi.RECUR_NO_REPEAT,
                 time = "5", next = 0):
        return self._add_record('task',
                     dict(name = name, project_hash = project_hash, context_hash = context_hash,
                          date = date, datetime = datetime, recur = recur, time = time, next = next))
    def update_task(self, record):
        return self._update_record('task', record.copy())

    def delete_task(self, record):
        return self._delete_record('task', record.copy())

    def add_note(self, name, body, project_hash, context_hash = "", date = ""):
        return self._add_record('note',
                         dict(name = name, body = body,
                              project_hash = project_hash, context_hash = context_hash, date = date))

    def update_note(self, record):
        return self._update_record('note', record.copy())

    def delete_note(self, record):
        return self._delete_record('note', record.copy())

    def _add_record(self, what, record):
        self._update_id += 1
        record['id'] = str(self._update_id)
        self._pending_updates[what].append(record)
        return record['id']

    def _update_record(self, what, record):
        self._update_id += 1
        record['id'] = str(self._update_id)
        record['flag'] = 'modified'
        record['ts'] =  datetime.datetime.now().strftime("%Y-%m-%d %T")
        self._pending_updates[what].append(record)
        return record['id']

    def _delete_record(self, what, record):
        self._update_id += 1
        record['id'] = str(self._update_id)
        record['flag'] = 'deleted'
        record['ts'] =  datetime.datetime.now().strftime("%Y-%m-%d %T")
        self._pending_updates[what].append(record)
        return record['id']

    def save_changes(self):
        """
        Saves to Nozbe all changes made by add_, update_, and delete_ methods.
        Returns deferred fired once the save is done. Flushes internal
        list.
        """
        updates = self._pending_updates
        self._reset_pending_updates()
        for key in updates.keys():
            if not updates[key]:
                del updates[key]
        return self.connection.post_request(self.api_url, "process", dev = self.app_id,
                                       POST = updates)

    def _reset_pending_updates(self):
        self._pending_updates = dict(project = [], task = [], context = [], tag = [], note = [])

    @classmethod
    def recur_label(cls, recur):
        """
        Returns textual description of recur (recursive task execution setting).
        For example maps 1 (RECUR_EVERY_DAY) to "Every day"
        """
        return cls.recur_labels[str(recur)]

    @defer.inlineCallbacks
    def _get_data(self, what, **extra):
        r = yield self.connection.get_request(self.api_url, "getdata", dev=self.app_id, what=what, **extra)
        defer.returnValue( r[what] )

class NozbeApi(NozbeSyncApi):
    """
    Aggregating information from both legacy and sync API.

    Works as NozbeSyncApi but extends data by items missing 
    there but present in legacy api. At the moment it only
    means extending project data with 'id' attribute (which, in turn,
    may be used to construct project page URL), everything
    else works as when NozbeSyncApi is directly used.
    """
    def __init__(self, *args, **kwargs):
        NozbeSyncApi.__init__(self, *args, **kwargs)
        self._legacy = NozbeLegacyApi(*args, **kwargs)

    @defer.inlineCallbacks
    def get_projects(self):
        """
        Extends projects with their id (which is of some use
        as it makes it possible to construct the "project page" url) -
        http://www.nozbe.com/account/projects/show-IDHERE
        """
        projects = yield NozbeSyncApi.get_projects(self)
        leg_projects = yield self._legacy.get_projects()
        for proj in projects:
            for lp in leg_projects:
                if proj['name'] == lp['name']:
                    proj[u'id'] = lp['id']
                    break
            if not proj['id']:
                log.warn("Couldn't find id for project '%s', link will not be available" % proj['name'])
        defer.returnValue(projects)
        
class CachingNozbeApi(NozbeApi):
    """
    Poor-man cache for Nozbe Api. Results of get_projects,
    get_contexts, get_tasks, get_completed_tasks, get_notes i
    get_uploads are cached and returned if the same function is called
    again. The cache is totally dumb and is never refreshed (not even
    after changes are submitted).

    The class is intented to be used in one-shot scripts (data exporters,
    graphics generators etc) where it may free programmer from passing
    things like "project list" between different functions.
    """
    def __init__(self, *args, **kwargs):
        NozbeApi.__init__(self, *args, **kwargs)
        self._cache = dict()
    def get_projects(self):
        return self._get_with_caching("projects", NozbeApi.get_projects)
    def get_contexts(self):
        return self._get_with_caching("contexts", NozbeApi.get_contexts)
    def get_tasks(self):
        return self._get_with_caching("tasks", NozbeApi.get_tasks)
    def get_completed_tasks(self):
        return self._get_with_caching("completed_tasks", NozbeApi.get_completed_tasks)
    def get_notes(self):
        return self._get_with_caching("notes", NozbeApi.get_notes)
    def get_uploads(self):
        return self._get_with_caching("uploads", NozbeApi.get_uploads)
    @defer.inlineCallbacks
    def _get_with_caching(self, name, method, *args, **kwargs):
        p = self._cache.get(name)
        if not p:
            p = yield method(self, *args, **kwargs)
            self._cache[name] = p
        defer.returnValue(p)
        
