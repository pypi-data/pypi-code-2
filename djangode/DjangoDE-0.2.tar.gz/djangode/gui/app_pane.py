# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from djangode import global_objects
from djangode.utils.qt import QtGui

class AppPane(QtGui.QWidget):
    def __init__(self, parent, app_name):
        QtGui.QWidget.__init__(self, parent)

        self.app_name = app_name

        self.layout = QtGui.QVBoxLayout()

        self.tree = QtGui.QTreeWidget(self)
        self.tree.itemDoubleClicked.connect(self.open_file)

        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

        self.build_tree()

    def build_tree(self):
        models = global_objects.project.module_contents("%s.models" % (self.app_name, ))

        if models is not None:
            models_top = QtGui.QTreeWidgetItem(self.tree)
            models_top.setText(0, "Models")

            for model_name in models:
                models_item = QtGui.QTreeWidgetItem(models_top)
                models_item.setText(0, model_name)

        views = global_objects.project.module_contents("%s.views" % (self.app_name, ))

        if views is not None:
            views_top = QtGui.QTreeWidgetItem(self.tree)
            views_top.setText(0, "Views")

            for views_name in views:
                views_item = QtGui.QTreeWidgetItem(views_top)
                views_item.setText(0, views_name)

    def open_file(self, tree_item):
        if tree_item.parent() is None:
            return

        item_name = tree_item.text(0)
        parent_name = tree_item.parent().text(0)

        file_name = global_objects.project.module_file("%s.%s" % (self.app_name, unicode(parent_name).lower()))

        global_objects.window.editor.open_file[(str, str)].emit(file_name, item_name)
