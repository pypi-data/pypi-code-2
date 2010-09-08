# Copyright (C) 2009-2010, Sandro Dentella <sandro@e-den.it>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk

from sqlkit import _

class SaveDialog(object):

    FILTER_FILES = (
        ( _('All files'), '*.*'),
        )

    def __init__(self,  title="Save dialog", default_filename='export.csv'):
        """
        A dialog to export data into a csv file

        :param default_filename: the default
        """

        self.dialog = gtk.FileChooserDialog(title,
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        self.dialog.set_default_response(gtk.RESPONSE_OK)
        self.dialog.set_current_name(default_filename)
        self.dialog.set_current_folder(self.current_folder())
        self.filename = None
        
        for name, pattern in self.FILTER_FILES:
            file_filter = gtk.FileFilter()
            file_filter.set_name(name)
            file_filter.add_pattern(pattern)
            self.dialog.add_filter(file_filter)
        
    
        ret = self.dialog.run()
        if ret == gtk.RESPONSE_OK:
            self.write()
        self.dialog.destroy()
        

    def current_folder(self):

        import platform
        import os

        CURRENT_FOLDER = ''
        if 'HOME' in os.environ:
            CURRENT_FOLDER = os.environ['HOME']
        elif platform.system() == "Windows":
            CURRENT_FOLDER = os.path.join(os.environ['USERPROFILE'], 'Desktop')

        return CURRENT_FOLDER
        
    def write(self):
        self.filename = self.dialog.get_filename()
        return

