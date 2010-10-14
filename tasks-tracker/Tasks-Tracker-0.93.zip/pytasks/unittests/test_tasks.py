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
from lib import tasks

printer = lambda msg: PRINTS.append(str(msg))

def setup_prints():
    global PRINTS
    
    PRINTS = []


# Change task file name for testing
tasks.TASK_FILE_NAME = 'taskunittestingfile'

def test_task_init():
    """Test task object init"""
    task = tasks.Task("testing tasks")
    
    assert_equal(task.desc, 'testing tasks')
    assert_equal(type(task.time), datetime)
    assert_equal(task.completed, False)
    

def test_task_status():
    """Test task status"""
    task = tasks.Task("testing tasks")
    
    assert_equal(task.status, 'Active')
    task.mark_as_completed()
    assert_equal(task.status, 'Completed')
    task.move_to_trash()
    assert_equal(task.status, 'Trashed')
    

def test_task_str():
    """Test tasks string output"""
    task = tasks.Task("testing tasks")
    assert_true('testing tasks' in task.__str__())
    
    
def test_task_mark_as_completed():
    """Test task mark as completed"""
    task = tasks.Task("testing tasks")
    
    assert_false(task.completed)
    task.mark_as_completed()
    assert_true(task.completed)

    
def test_task_mark_as_active():
    """Test task mark as active"""
    task = tasks.Task("testing tasks")
    
    task.mark_as_completed()
    assert_false(task.active)
    
    task.mark_as_active()
    assert_true(task.active)


def test_task_move_to_trash():
    """Test task move to trash"""
    task = tasks.Task("testing tasks")
    
    assert_false(task.trashed)
    task.move_to_trash()
    assert_true(task.trashed)
    

def test_task_restore_from_trash():
    """Test task restore from trash"""
    task = tasks.Task("testing tasks")
    
    task.move_to_trash()
    assert_true(task.trashed)
    task.restore_from_trash()
    assert_false(task.trashed)
    assert_true(task.active)
    

def test_initialisation():
    """Test initialisation"""
    assert_false(tasks.is_initialized())
    tasks.initialize()
    assert_true(tasks.is_initialized())
    tasks.un_initialize()
    assert_false(tasks.is_initialized())


@with_setup(tasks.initialize, tasks.un_initialize)
def test_get_all_tasks():
    """Test get all tasks"""
    assert_equal(len(tasks.get_all_tasks()), 0)
    tasks.add_task('test_task')
    assert_equal(len(tasks.get_all_tasks()), 1)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_get_active_tasks():
    """Test get active tasks"""
    assert_equal(len(tasks.get_active_tasks()), 0)
    tasks.add_task('test_task')
    assert_equal(len(tasks.get_active_tasks()), 1)
    

@with_setup(tasks.initialize, tasks.un_initialize)
def test_get_completed_tasks():
    """Test completed tasks"""
    assert_equal(len(tasks.get_completed_tasks()), 0)
    tasks.add_task('test_task')
    tasks.mark_as_completed(0)
    assert_equal(len(tasks.get_completed_tasks()), 1)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_trashed_tasks():
    """Test trashed tasks"""
    assert_equal(len(tasks.get_trashed_tasks()), 0)
    tasks.add_task('test_task')
    tasks.move_to_trash(0)
    assert_equal(len(tasks.get_trashed_tasks()), 1)
    tasks.restore_from_trash(0)
    assert_equal(len(tasks.get_trashed_tasks()), 0)
    

@with_setup(tasks.initialize, tasks.un_initialize)
def test_save_all_tasks():
    """Test save all tasks"""
    tasks.save_all_tasks([])
    assert_equal(len(tasks.get_all_tasks()), 0)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_add_task():
    """Test add task"""
    tasks.add_task('test new task')
    assert_equal(len(tasks.get_all_tasks()), 1)
    

@with_setup(tasks.initialize, tasks.un_initialize)
def test_move_to_trash():
    """Test move to trash"""
    tasks.add_task('test new task')
    tasks.move_to_trash(0)
    assert_equal(len(tasks.get_trashed_tasks()), 1)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_restore_from_trash():
    """Test restore from trash"""
    tasks.add_task('test new task')
    tasks.move_to_trash(0)
    assert_equal(len(tasks.get_trashed_tasks()), 1)
    tasks.restore_from_trash(0)
    assert_equal(len(tasks.get_trashed_tasks()), 0)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_empty_trash():
    """Test empty trash"""
    tasks.add_task('test new task')
    tasks.move_to_trash(0)
    assert_equal(len(tasks.get_trashed_tasks()), 1)
    tasks.empty_trash()
    assert_equal(len(tasks.get_trashed_tasks()), 0)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_mark_as_completed():
    """Test mark as completed"""
    tasks.add_task('test new task')
    assert_equal(len(tasks.get_completed_tasks()), 0)
    tasks.mark_as_completed(0)
    assert_equal(len(tasks.get_completed_tasks()), 1)
    
    
@with_setup(tasks.initialize, tasks.un_initialize)
def test_mark_as_active():
    """Test mark as active"""
    tasks.add_task('test new task')
    tasks.mark_as_completed(0)
    assert_equal(len(tasks.get_active_tasks()), 0)
    tasks.mark_as_active(0)
    assert_equal(len(tasks.get_active_tasks()), 1)


@with_setup(tasks.initialize, tasks.un_initialize)
def test_archive_tasks():
    """Test archive completed tasks"""
    tasks.add_task('test new task')
    tasks.mark_as_completed(0)
    assert_equal(len(tasks.get_completed_tasks()), 1)
    
    tasks.archive_tasks()
    assert_equal(len(tasks.get_completed_tasks()), 0)


@with_setup(tasks.initialize, tasks.un_initialize)
@with_setup(setup_prints)
def test_list_all_tasks():
    """Test list all tasks"""
    tasks.add_task('testing')
    tasks.list_all_tasks(printer)
    
    assert_equal(len(PRINTS), 1)
    

@with_setup(tasks.initialize, tasks.un_initialize)
@with_setup(setup_prints)
def test_list_active_tasks():
    """Test list active tasks"""    
    tasks.add_task('test task')
    tasks.list_active_tasks(printer)
    
    assert_equal(len(PRINTS), 2)
    assert_true('Active tasks' in PRINTS[0])
    assert_true('test task' in PRINTS[1])
    
    
@with_setup(tasks.initialize, tasks.un_initialize)
@with_setup(setup_prints)
def test_list_completed_tasks():
    """Test list completed tasks"""
    tasks.add_task('test task')
    tasks.mark_as_completed(0)
    tasks.list_completed_tasks(printer)
    
    assert_equal(len(PRINTS), 2)
    assert_true('Completed tasks' in PRINTS[0])
    assert_true('test task' in PRINTS[1])


@with_setup(tasks.initialize, tasks.un_initialize)
@with_setup(setup_prints)
def test_list_trashed_tasks():
    """Test list trashed tasks"""
    tasks.add_task('test task')
    tasks.move_to_trash(0)
    tasks.list_trashed_tasks(printer)
    
    assert_equal(len(PRINTS), 2)
    assert_true('Tasks in trash' in PRINTS[0])
    assert_true('test task' in PRINTS[1])


@with_setup(tasks.initialize, tasks.un_initialize)
@with_setup(setup_prints)
def test_list_with_index():
    """Test list with index"""
    tasks.INDEXED = True
    tasks.add_task('test task')
    tasks.add_task('test task two')
    
    tasks.list_active_tasks(printer)
    
    assert_true('1' in PRINTS[1])
    assert_true('2' in PRINTS[2])


@with_setup(tasks.initialize, tasks.un_initialize)
@with_setup(setup_prints)
def test_list_detailed():
    """Test list with index"""
    tasks.DETAIL_DISPLAY = True
    tasks.add_task('test task')
    
    tasks.list_active_tasks(printer)
    
    date_str = datetime.now().strftime(tasks.TIME_DISPLAY_FORMAT)
    assert_true(date_str in PRINTS[1])


if __name__ == '__main__': #pragma no coverage
    import nose

    nose_config = nose.config.Config()
    nose_config.verbosity=2

    nose.runmodule(config=nose_config)