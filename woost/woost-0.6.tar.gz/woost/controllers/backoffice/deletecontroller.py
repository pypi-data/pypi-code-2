#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from ZODB.POSException import ConflictError
from cocktail.modeling import getter, cached_getter, InstrumentedSet
from cocktail.translations import translations
from cocktail.schema import (
    String,
    Collection,
    Reference,
    RelationMember,
    remove
)
from cocktail.persistence import datastore, PersistentClass
from woost.models import (
    changeset_context,
    delete_validating,
    get_current_user,
    DeletePermission
)
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.editstack import EditNode
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class DeleteController(BaseBackOfficeController):
    
    MAX_TRANSACTION_ATTEMPTS = 3

    _delete_dry_run_done = False

    def __init__(self, *args, **kwargs):
        BaseBackOfficeController.__init__(self, *args, **kwargs)

        self._delete_tree = []
        self._blocking_members = []

    @cached_getter
    def selection(self):
        """The selected subset of items that should be deleted.
        @type: L{Item<woost.models.item.Item>} collection
        """
        return self.params.read(
            Collection("selection", items = "woost.models.Item"))

    def _delete_dry_run(self):

        if self._delete_dry_run_done:
            return

        visited = set()

        def recurse(item, container):

            if item in visited:
                return
            
            visited.add(item)
            deleted_descendants = list()
            container.append((item, deleted_descendants))
            
            for member in item.__class__.members().itervalues():

                if isinstance(member, RelationMember) \
                and member.related_type \
                and isinstance(member.related_type, PersistentClass):
                    
                    if member.block_delete and item.get(member):
                        self._blocking_members.append((item, member))

                    if item._should_cascade_delete(member):
                        value = item.get(member)

                        if value is not None:
                            if isinstance(member, Reference):
                                value = (value,)

                            member_container = list()
                            for descendant in value:
                                if descendant is not None:
                                    recurse(descendant, member_container)
       
                            if len(member_container) > 0:
                                deleted_descendants.append(
                                    (member, member_container)
                                )

        for item in self.selection:
            recurse(item, self._delete_tree)
        
        self._delete_dry_run_done = True

    @getter
    def delete_tree(self):
        self._delete_dry_run()
        return self._delete_tree

    @getter
    def blocking_members(self):
        self._delete_dry_run()
        return self._blocking_members

    @cached_getter
    def action(self):
        """A string identifier indicating the action that has been activated by
        the user.
        @type: str or None
        """
        return self.params.read(String("action"))

    @cached_getter
    def submitted(self):
        return self.action is not None
    
    def submit(self):
        # Load the edit stack before deleting any item, to ensure its
        # loaded properly
        stack = self.edit_stack

        if self.action == "confirm_delete":
            
            user = get_current_user()

            for i in range(self.MAX_TRANSACTION_ATTEMPTS):

                deleted_set = None

                with changeset_context(author = user):
                    for item in self.selection:
                        deleted_set = delete_validating(
                            item,
                            deleted_set = deleted_set
                        )

                try:
                    datastore.commit()
                except ConflictError:
                    datastore.abort()
                    datastore.sync()
                else:
                    break       
          
            # Purge the edit stack of references to deleted items
            if stack:
                prev_stack_size = len(stack)
                stack.remove_references(deleted_set)
            
            # Launch CMS.item_deleted events
            cms = self.context["cms"]

            for item in deleted_set:
                cms.item_deleted(
                    item = item,
                    user = user,
                    change = item.changes[-1] if item.changes else None
                )

            # If the edit stack has been modified as a result of the delete
            # operation (an edited item has been deleted), redirect the user
            # to the topmost edit node, or to the application root
            if stack is not None and len(stack) < prev_stack_size:

                while len(stack) > 0 \
                and not isinstance(stack[-1], EditNode):
                    stack.pop()
                
                notify_user(
                    translations(
                        "woost.controllers.DeleteController."
                        "node_deleted_notice"
                    ),
                    category = "error",
                    transient = True
                )

        if stack:
            stack.go()
        else:
            self.go_back()
            

    view_class = "woost.views.BackOfficeDeleteView"

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output["delete_tree"] = self.delete_tree
        output["blocking_members"] = self.blocking_members
        return output

