# -*- coding: utf-8 -*-

class RtmUpdater(object):
    """
    Class responsible for creating new lists, tags, and tasks.
    Apart from wrapping RememberTheMilk API quirks it handles
    duplicate detection in case of lists and tags.

    All updates are performed inside single timeline (Rtm undo
    context) unless set_undo_point routine is called.
    """
    
    def __init__(self, api):
        """
        Initializes object. 

        Parameters
        ----------

        - `api` - authorized RtmApi object used to handle communication.
        """
        self.api = api
        self._list_cache = None     # name -> id, created on first use
        self._tag_cache = dict()    # name -> id
        self._timeline = None

    def find_or_create_list(self, list_name):
        """
        Looks for the list of given name. If such list does not exist, creates
        it. Returns list_id.
        """
        self._load_list_cache_if_necessary()
        id = self._list_cache.get(list_name)
        if id:
            return id
        timeline = self._get_timeline()

        r = self.api.rtm.lists.add(timeline = timeline,
                                   name = list_name)
        id = r.list.id
        self._list_cache[list_name] = id
        return id

    def known_lists(self):
        """
        Returns all known lists (except smartlists, only true lists are returned).

        Return value is a list of pairs (list_id, list_name)
        """
        self._load_list_cache_if_necessary()
        return [ (id, name) for name, id in self._list_cache.iteritems() ]

    def create_task(self, task_name,
                    list_id = None,
                    tags = [], 
                    completed = False,
                    priority = None,
                    due_date = None,
                    estimate = None,
                    repeat = None,
                    url = None,
                    notes = [],
                    ):
        """
        Creates new task and sets some attributes. Returns pair (taskseries_id, task_id).

        :Parameters:
        - task_name 
        - list_id - list identifier or None for Inbox
        - tags - list of tags (note: names can't contain ',')
        - completed - is task already completed
        - priority - 1, 2, or 3
        - due_date - due date (will be parsed, usually ISO 8601 format should work)
        - estimate - estimated cost (text like "3 days 2 hours 40 minutes")
        - repeat - task repeat. Text like "Every Tuesday", "Every month on the 4th", "Every week until 1/1/2007",
                "After a week" etc. See http://www.rememberthemilk.com/help/answers/basics/repeatformat.rtm
        - url - url related to the task
        - notes - list of pairs (title, text)

        :Return:
        - pair of (taskseries_id, task_id)
        """
        timeline = self._get_timeline()
        if list_id:
            r = self.api.rtm.tasks.add(timeline = timeline,
                                       list_id = list_id,
                                       name = task_name)
        else:
            r = self.api.rtm.tasks.add(timeline = timeline,
                                       name = task_name)
        task_id = r.list.taskseries.task.id
        taskseries_id = r.list.taskseries.id
        if not list_id:
            # addTags and other methods require it
            list_id = r.list.id

        if tags:
            tag_text = ", ".join(tags)
            self.api.rtm.tasks.addTags(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                tags = tag_text)

        if completed:
            self.api.rtm.tasks.complete(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id)

        if priority:
            self.api.rtm.tasks.setPriority(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                priority = str(priority))

        if due_date:
            self.api.rtm.tasks.setDueDate(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                due = due_date, parse = "1", # has_due_time = 1
                )

        if estimate:
            self.api.rtm.tasks.setEstimate(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                estimate = estimate,
                )

        if repeat:
            self.api.rtm.tasks.setRecurrence(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                repeat = repeat,
                )
            
        if url:
            self.api.rtm.tasks.setURL(
                timeline = timeline,
                list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                url = url)

        for (note_title, note_text) in notes:
            self.add_task_note(list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
                               note_title = note_title, note_text = note_text)

        return (taskseries_id, task_id)

    def add_task_note(self, 
                      list_id, taskseries_id, task_id,
                      note_title, note_text):
        """
        Adds new note to the task. 

        Parameters
        ----------

        `list_id`, `taskseries_id`, `task_id` - necessary list and task identifiers
        `note_title`, `note_text` - title and text of new note
        """
        timeline = self._get_timeline()
        self.api.rtm.tasks.notes.add(
            timeline = timeline,
            list_id = list_id, taskseries_id = taskseries_id, task_id = task_id,
            note_title = note_title, note_text = note_text)

    def set_undo_point(self):
        # Just forgetting previous timeline. New one will be created before first update
        self._timeline = None

    def _get_timeline(self):
        if self._timeline is None:
            r = self.api.rtm.timelines.create()
            self._timeline = r.timeline.value
        return self._timeline

    def _load_list_cache_if_necessary(self):
        if self._list_cache is None:
            r = self.api.rtm.lists.getList()
            cache = {}
            for l in r.lists:
                if not int(l.smart):
                    cache[l.name] = l.id
            self._list_cache = cache


"""
Useful examples:

    # get all open tasks, see http://www.rememberthemilk.com/services/api/methods/rtm.tasks.getList.rtm
    result = api.rtm.tasks.getList(filter="status:incomplete")
    for tasklist in result.tasks:
        for taskseries in tasklist:
            print taskseries.task.due, taskseries.name

    # Create new list
    result = api.rtm.lists.add(timeline = timeline,
                               name = u"Zażółć gęślą test")
    list_id = result.list.id
    print "Created list with id", list_id

    # And task
    result = api.rtm.tasks.add(timeline = timeline,
                               list_id = list_id,
                               name = u"Żółć gęśą zajaźniam")
    task_id = result.list.taskseries.task.id
    print task_id
    print "Created task", task_id



"""
