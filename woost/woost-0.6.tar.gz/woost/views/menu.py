#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.html import templates, Element
from cocktail.controllers import context
from woost.models import Site

TreeView = templates.get_class("cocktail.html.TreeView")


class Menu(TreeView):
    """A visual component used to render navigation menus and site maps.
    
    @var root_visible: If set to True, the produced tree has a single root.
        Otherwise, the root element is hidden and the tree appears to have
        multiple roots instead.
    @type root_visible: bool

    @var selection: Indicates the selected item.
    @type selection: L{Publishable<woost.models.publishable.Publishable>}

    @var emphasized_selection: When set to True, adds a <strong> tag to
        highlight the selected item.
    @type emphasized_selection: bool

    @var linked_selection: Indicates if the entry for the selected item should
        behave as a link or not.
    @type linked_selection: bool
    
    @var linked_containers: Indicates if entries that contain other entries
        should behave as links.
    @type linked_containers: bool

    @var max_depth: The maximum depth for the menu.
    @type max_depth: int

    @var expanded: When set to True, the menu will be completely expanded. When
        False, entries will only be expanded if they contain the selected
        entry.
    @type expanded: bool
    """
    root_visible = False
    selection = None
    emphasized_selection = True
    linked_selection = True
    linked_containers = True
    max_depth = None
    expanded = False

    def _ready(self):

        self._cms = context["cms"]

        if self.root is None:
            self.root = Site.main.home

        if self.selection is None:
            self.selection = context["publishable"]
        
        # Find the selected path
        self._expanded = set()
        item = self.selection

        while item is not None:
            self._expanded.add(item)
            item = item.parent

        # Limited depth
        self._depth = 2 if self.root_visible else 1

        TreeView._ready(self)
    
    def filter_item(self, item):
        return not item.hidden and item.is_accessible()

    def get_item_uri(self, item):
        return self._cms.uri(item)

    def create_entry(self, item):
        entry = TreeView.create_entry(self, item)

        if item in self._expanded:
            entry.add_class("selected")

        return entry

    def create_label(self, item):
        
        if self.should_link(item):
            label = Element("a")
            label["href"] = self.get_item_uri(item)
        else:
            label = Element("span")
        
        label.append(self.get_item_label(item))

        if self.emphasized_selection and item is self.selection:
            if label.tag == "a":
                label = Element("strong", children = [label])
            else:
                label.tag = "strong"

        return label

    def should_link(self, item):
        return (self.linked_selection or item is not self.selection) \
            and (self.linked_containers or not item.children)

    def get_child_items(self, parent):

        if (self.max_depth is not None and self._depth > self.max_depth) \
        or (not self.expanded and parent not in self._expanded):
            return []
        else:
            return TreeView.get_child_items(self, parent)

    def _fill_children_container(self, container, item, children):
        self._depth += 1
        TreeView._fill_children_container(self, container, item, children)
        self._depth -= 1        

