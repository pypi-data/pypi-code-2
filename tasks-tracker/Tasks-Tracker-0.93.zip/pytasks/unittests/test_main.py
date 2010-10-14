__copyright__ = """
    This file is part of Tasks-Tracker.

    Tasks-Tracker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Tasks-Tracker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Tasks-Tracker.  If not, see <http://www.gnu.org/licenses/>.
"""


from nose.tools import *
from datetime import datetime
from pytasks.lib import tasks
from pytasks import main as tasks_main

import os

printer = lambda msg: PRINTS.append(str(msg))

# Change task file name for testing
tasks.TASK_FILE_NAME = 'taskunittestingfile'

def setup_test():
    global PRINTS
    
    PRINTS = []

    if os.path.exists(tasks.TASK_FILE_NAME):
        os.remove(tasks.TASK_FILE_NAME)
        
        
def tear_down():
    if os.path.exists(tasks.TASK_FILE_NAME):
        os.remove(tasks.TASK_FILE_NAME)
    

@with_setup(setup_test, tear_down)
def test_command_init():
    """Test main - command init"""
    
    tasks_main.command_init(printer)
    
    assert_equal(len(PRINTS), 1)
    assert_equal('Initializing tasks in current folder.', PRINTS[0])
    
    tasks_main.command_init(printer)
    assert_equal('Current folder has already been setup. Use --reset to reset all tasks', PRINTS[1])
    

if __name__ == '__main__': #pragma no coverage
    import nose

    nose_config = nose.config.Config()
    nose_config.verbosity=2

    nose.runmodule(config=nose_config)