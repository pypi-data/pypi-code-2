"""Main module to run app"""

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

import sys, os

from lib import tasks
from lib.versionlib import get_version

DESCRIPTION = """Task-Tracker %(version)s -- A simple command line project task tracking tool.
https://launchpad.net/tasks-tracker
""" % {'version': get_version().current_release()}

def command_init(printer):
    if tasks.is_initialized():
        printer('Current folder has already been setup. Use --reset to reset all tasks')
    else:
        printer('Initializing tasks in current folder.')
        tasks.initialize()


def command_reset(printer):
    confirm = raw_input('\nAll saved tasks will be lost. [y] to continue, [n] to cancel: ')
    if confirm is 'y':
        tasks.initialize()
        printer('Tasks has been reset successfully')
    else:
        printer('Operation canceled')


def command_un_init(printer):
    confirm = raw_input('\nAll saved tasks will be lost. [y] to continue, [n] to cancel: ')
    if confirm is 'y':
        tasks.un_initialize()
        printer('Tasks has been un-initialized for current folder')
    else:
        printer('Operation canceled')


def command_empty_trash(printer):
    confirm = raw_input('\nAll tasks in trash will be lost. [y] to continue, [n] to cancel: ')
    if confirm is 'y':
        tasks.empty_trash()
        printer('Trash is now empty')
    else:
        printer('Operation canceled')


def command_archive_completed(printer):
    confirm = raw_input('\nMove all completed tasks to trash. [y] for YES, [n] for NO: ')
    if confirm is 'y':
        tasks.archive_tasks()
        printer('All completed tasks moved to trash')
    else:
        printer('Operation canceled')


def run_commands(options, printer):
    options.init and command_init(printer)
    
    if not tasks.is_initialized():
        printer("Please initialize tasks in the current folder using --init.")
        return 
    
    if options.un_init:
        command_un_init(printer)
        return
    
    options.reset and command_reset(printer)
    
    options.new and tasks.add_task(options.new)
    
    tasks.DETAIL_DISPLAY = options.show_detail
    tasks.INDEXED = options.indexed
    
    if options.remove:
        tasks.INDEXED = True
        tasks.list_all_tasks(printer=printer)
        task_index = raw_input('\nEnter the index of task to be deleted (moved to the trash): ')
        tasks.move_to_trash(int(task_index) - 1)
    
    if options.done:
        tasks.INDEXED = True
        tasks.list_active_tasks(printer=printer)
        task_index = raw_input('\nEnter the index of task that is completed: ')
        tasks.mark_as_completed(int(task_index) - 1)    
    
    if options.un_done:
        tasks.INDEXED = True
        tasks.list_all_tasks(printer=printer)
        task_index = raw_input('\nEnter the index of task to set active: ')
        tasks.mark_as_active(int(task_index) - 1)
    
    options.empty_trash and command_empty_trash(printer=printer)
    options.archive and command_archive_completed(printer=printer)
    
    options.show_completed and tasks.list_completed_tasks(printer=printer)
    options.show_all and tasks.list_all_tasks(printer=printer)
    options.show_trash and tasks.list_trashed_tasks(printer=printer)
    
    if not options.show_all and not options.show_completed and not options.show_trash:
        tasks.list_active_tasks(printer=printer)


def run_recursive(options, printer):
    curr_dir = os.getcwd()
    for root, directory, files in os.walk('.'):
        os.chdir(root)
        
        if tasks.is_initialized():
            printer('----- Tasks in directory [%s]' % root)
            try: 
                run_commands(options, printer)
            except Exception, err: 
                printer(str(err.message))
            printer('')
            
        os.chdir(curr_dir)
        
    
def run(): 
    from optparse import OptionParser, OptionGroup
    
    import logging
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    parser = OptionParser(description=DESCRIPTION, 
                          prog='tasks',
                          usage='%prog [-n TASK] ', 
                          version="Tasks-Tracker %s" % get_version().current_release())

    parser.add_option('-R', '--recursive', action="store_true", dest='recursive', 
                      help="""run commands recursively in sub-folders""", default=False)
    
    setup_group = OptionGroup(parser, "Setup commands")
    setup_group.add_option('', '--init', action="store_true", dest="init", 
                           help="""initialize tasks in folder""", default=False)
    setup_group.add_option('', '--un-init', action="store_true", dest="un_init", 
                           help="""un-initialize tasks for current folder (Removes .tasks file).""", default=False)
    setup_group.add_option('', '--reset', action="store_true", dest="reset", 
                           help="""initialize new tasks in folder, loses all previous tasks""", default=False)
    setup_group.add_option('', '--empty-trash', action="store_true", dest='empty_trash', 
                           help="""permanently delete tasks in trash""", default=False)
    setup_group.add_option('', '--archive', action="store_true", dest='archive', 
                           help="""move all completed tasks to trash""", default=False)
    
    basic_group = OptionGroup(parser, "Basic tasks commands")
    basic_group.add_option('-n', '--new', dest='new', 
                           help="""create a new task""", default=None)
    basic_group.add_option('-c', '--completed', action="store_true", dest='done', 
                           help="""set a task as completed""", default=False)
    basic_group.add_option('-d', '--delete', action="store_true", dest='remove', 
                           help="""move a task to the trash""", default=False)
    basic_group.add_option('-a', '--active', action="store_true", dest='un_done', 
                           help="""set a task as active""", default=False)
    
    list_group = OptionGroup(parser, "List commands")
    list_group.add_option('', '--indexed', action="store_true", dest='indexed', 
                          help="""show index when listing tasks""", default=False)
    list_group.add_option('', '--detail', action="store_true", dest='show_detail', 
                          help="""show more details when listing tasks""", default=False)
    list_group.add_option('-C', '--show-completed', action="store_true", dest='show_completed', 
                          help="""show only completed tasks""", default=False)
    list_group.add_option('-D', '--show-deleted', action="store_true", dest='show_trash', 
                          help="""show trashed tasks""", default=False)
    list_group.add_option('-A', '--show-all', action="store_true", dest='show_all', 
                          help="""show all tasks (active, completed and trashed)""", default=False)
    
    
    parser.add_option_group(setup_group)
    parser.add_option_group(basic_group)
    parser.add_option_group(list_group)

    options, args = parser.parse_args()
    
    PRINTER = logging.info
    
    PRINTER("")
    func = options.recursive and run_recursive or run_commands
    func(options, PRINTER)
    show_minimized_help(PRINTER)


def show_minimized_help(printer):
    printer("\n")
    printer("Tips: -n new task | -c completed | -d delete | -a mark as active | -h help")


if __name__ == "__main__":
    sys.exit(run())