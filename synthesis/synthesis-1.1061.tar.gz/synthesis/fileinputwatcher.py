'''
This module watches multiple directories for new files and notifies \
when a new file encountered.  It has POSIX and win32 versions.  \
The POSIX version uses a queue to run the watch as a thread and \
make a non-polling notification.
'''
# The MIT License
# 
# Copyright (c) 2007 Suncoast Partnership 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

global osiswin32
#import selector

import os, time, exceptions
from time import sleep
from conf import settings

# determine what environment we are running under, win32 or POSIX
if os.name == 'nt':   
    osiswin32 = True
    try:
        import win32file
        import win32event
        import win32con
    except ImportError:
        print 'Could not import win32 modules.'     
                
else:
    osiswin32 = False
    try:
        import pyinotify
        from pyinotify import WatchManager, ThreadedNotifier, ProcessEvent, EventsCodes
    except ImportError:
        print 'Could not import POSIX pyinotify modules.'


class FileInputWatcher:
    '''controlling class for file monitoring'''

    def __init__(self, dir_to_watch, queue): 
        print 'FileInputWatcher Initialized'
        # SBB20090903 Adding debugging capability, not processing multiple file drops into multiple directories.
        if settings.DEBUG:
            print '*************Debugging On*************'
        
        self.queue = queue
        self.dir_to_watch = dir_to_watch
        
        # make a notifier (nothing)
        self.notifier1 = None
        self.notifier2 = None
                
    def monitor(self):
        '''The command to start monitoring a directory or set of them.'''
        print 'Monitoring Directories: %s' % self.dir_to_watch
        print "Watching started at %s" % (time.asctime())
        if osiswin32:
            print 'Watching win32 OS'              
            return self.watch_win32(self.dir_to_watch)
        else:
            print 'Watching POSIX OS'
            #if settings.DEBUG:
                #print 'sending to self.watch_posix_start()'
            self.watch_posix_start()
            #if settings.DEBUG:
                #print "It returned from self.watch_posix_start()!"
                #print "self.watch_posix_start() returned with value", result
        return True
    
    def stop_monitoring(self):  
        '''os independent method to stop monitoring, but only posix uses it.'''
        #print "self.notifier1.started", self.notifier1.__getattribute__('started')
        if isinstance(self.notifier1, ThreadedNotifier):
            #if settings.DEBUG:
                #print "self.notifier1 is an instance"
            if isinstance(self.notifier2, ThreadedNotifier):
                #if settings.DEBUG:
                    #print "self.notifier2 is an instance"
                self.watch_posix_stop()
                
        else: 
            if settings.DEBUG:
                print "notifiers were not instantiated, so not calling self.watch_posix_stop() again"
        print 'Done Monitoring'
                
    def watch_win32(self, dir_to_watch): 
        '''os-specific watch command'''
        # Loop forever, listing any file changes. The WaitFor... will
        #  time out every half a second allowing for keyboard interrupts
        #  to terminate the loop.    
        files_added = []
        old_path_contents = []
        new_path_contents = []
        cnt = 0
        try:
            while 1:
                cnt += 1
                #print 'Watching %s' % cnt           
                #old_path_contents = os.listdir(dirToWatch)
                for item in dir_to_watch:
                    change_handle = win32file.FindFirstChangeNotification(item, 0, win32con.FILE_NOTIFY_CHANGE_FILE_NAME)
                    old_path_contents.append(os.listdir(item))               
                result = win32event.WaitForSingleObject(change_handle, 500)
                # If the WaitFor... returned because of a notification (as
                #  opposed to timing out or some error) then look for the
                #  changes in the directory contents.
                if result == win32con.WAIT_OBJECT_0:
                    #new_path_contents = os.listdir(dirToWatch)
                    # build the new list with all the files from all dirs
                    for item in dir_to_watch:
                        new_path_contents.append(os.listdir(item))             
                    files_added = [f for f in new_path_contents if not f in old_path_contents]
                    #files_deleted = [f for f in old_path_contents if not f in new_path_contents]      
                    if files_added:
                        print
                        print time.asctime ()
                        print "Added:", files_added or "Nothing"
                        return files_added
                    #print "Deleted:", files_deleted or "Nothing"           
                win32file.FindNextChangeNotification(change_handle)
        except KeyboardInterrupt:
            return []
        #finally:
        #	win32file.FindCloseChangeNotification(change_handle)
            
    def watch_posix_start(self): 
        '''os-specific command to watch'''
        
        # test to see if we already have a notifier object, if not, make it, otherwise we are already watching a set of folders
        if self.notifier1 == None and self.notifier2 == None:
            
            try:
                pyinotify.compatibility_mode()
                print 'pyinotify running in compatibility mode'
            except:
                print 'pyinotify running in standard mode'
            try:
                #mask = EventsCodes.IN_CREATE |EventsCodes.IN_MOVED_TO 
                mask = pyinotify.ALL_EVENTS
                #ECJ20100831 Reason why we have two threads: it never returns control ever to the main loop if only one thread, so no ctrl+c
                #The second thread is a dummy, so it performs switching/relinquishing control
                #Eventually, we want to watch many folders, so that is why we are using the ThreadedNotifier, versus the recommended Notifier.
                #Even then, Notifier is still probably the way to go, but we'll use this as long as it works, because then you don't have to poll/While loop
                
                # Thread #1
                watch_manager1 = WatchManager()
                self.notifier1 = ThreadedNotifier(watch_manager1, EventHandler(self.queue))
                self.notifier1.start()
                print 'Starting the threaded notifier on ', self.dir_to_watch
                watch_manager1.add_watch(self.dir_to_watch, mask)
                # Thread #2
                watch_manager2 = WatchManager()
                self.notifier2 = ThreadedNotifier(watch_manager2, EventHandlerDummy(self.queue))
                self.notifier2.start()
                #just watch any place, but don't remove this or Ctrl+C will not work
                watch_manager2.add_watch(settings.BASE_PATH, mask)
                if settings.DEBUG:
                    print "both notifiers started"
            
            except KeyboardInterrupt:
                print "Keyboard Interrupt in notifier"
                self.notifier1.stop()
                self.notifier2.stop()
                
                return
            except NameError:
                self.notifier1.stop()
                self.notifier2.stop()
                return ['POSIX Watch Error']
            except:
                print "General exception caught within notifier while loop, stopping both notifiers now"
                self.notifier1.stop()
                self.notifier2.stop()
                
                # SBB20090903 Turn on verbose mode
                self.notifier1.VERBOSE = settings.DEBUG
                print "returning to calling function"
                return True
            
    def watch_posix_stop(self):
        'os specific call to stop monitoring'
        print 'Stopping the threaded notifiers.'
        self.notifier1.stop()
        print "stopped self.notifier1.stop()"
        self.notifier2.stop()
        print "stopped self.notifier2.stop()"
        return
          
class EventHandler(ProcessEvent): 
    '''Event handler processing create events passed in to the \
    watch manager by the notifier.''' 
    def __init__(self, queue):
        self.queue = queue
            
    def process_IN_CREATE(self, event):
        '''What happens when a file is added'''
        if event.name[0] == '.':
            print 'ignoring ', event.name
        else:
            print "Create: %s" %  os.path.join(event.path, event.name)
            self.queue.put(os.path.join(event.path, event.name))
            #print "queue is now", self.queue
        
    def process_IN_MOVED_TO(self, event):
            '''What happens when a file is added'''
            if event.name[0] == '.':
                print 'ignoring ', event.name
            else:
                print "In_Moved_To: %s" %  os.path.join(event.path, event.name)
                self.queue.put(os.path.join(event.path, event.name))
                print "queue is now", self.queue
        
class EventHandlerDummy(ProcessEvent): 
    '''Event handler processing create events passed in to the \
    watch manager by the notifier.''' 
    def __init__(self, queue):
        self.queue = queue
            
    def process_IN_CREATE(self, event):
        '''What happens when a file is added'''
        print "Create: %s" %  os.path.join(event.path, event.name)
        