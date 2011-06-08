############################################################
#	FileName	spin.py
__author__ =	"Branimir Petrovic"
__version__ =	"1.0.0"
__date__ =		"1 Feb 2003"
############################################################

import sys, threading, time

class ProgressBase(threading.Thread):
    """Base class - not to be instanciated."""

    def __init__(self):
        self.rlock = threading.RLock()
        self.cv = threading.Condition()
        threading.Thread.__init__(self)
        self.setDaemon(1)

    def __backStep(self):
        if self.inplace: sys.stdout.write('\b \b')

    def __call__(self):
        self.start()

    def start(self):
        self.stopFlag = 0
        threading.Thread.start(self)

    def stop(self):
        """To be called by the 'main' thread: Method will block
        and wait for the thread to stop before returning control
        to 'main'."""

        self.stopFlag = 1

        # Wake up 'Sleeping Beauty' ahead of time (if it needs to)...
        self.cv.acquire()
        self.cv.notify()
        self.cv.release()

        # Block and wait here untill thread fully exits its run method.
        self.rlock.acquire()




class Spinner(ProgressBase):
    """Print 'animated' /|\ sequence to stdout in separate thread"""

    def __init__(self, speed=0.1):
        #self.__seq = [chr(47), "|", chr(92)]
        self.__seq = ['.    ', '..   ', '...  ', '.... ', '.....', ' ....', '  ...', '   ..', '    .']
        self.__speed = speed
        self.inplace = 1
        ProgressBase.__init__(self)

    def run(self):
        self.rlock.acquire()
        self.cv.acquire()
        sys.stdout.write(' ')
        while 1:
            for char in self.__seq:
                self.cv.wait(self.__speed)  # 'Sleeping Beauty' part
                if self.stopFlag:
                    self._ProgressBase__backStep()
                    try :
                        return                          ### >>>
                    finally :
                        # release lock immediatley after returning
                        self.rlock.release()
                if self.inplace: sys.stdout.write('\b' * len(char))
                sys.stdout.write(char)
                sys.stdout.flush()
       

class Dotter(ProgressBase):
    """Print 'animated' sequence of dots - one per sec."""

    def __init__(self, speed=1):
        self.__seq = "."
        self.__speed = speed
        self.inplace = 0
        ProgressBase.__init__(self)

    def run(self):
        self.cv.acquire()
        self.rlock.acquire()
        while 1:
            self.cv.wait(self.__speed)      # 'Sleeping Beauty' part
            if self.stopFlag:
                self._ProgressBase__backStep()
                try :
                    return                              ### >>>
                finally :
                    # release lock immediatley after returning
                    self.rlock.release()
            if self.inplace: sys.stdout.write('\b')
            sys.stdout.write(self.__seq)
            sys.stdout.flush()


def spinIt(fnct, *args, **kwargs):
    """Displays spinner while the fnct executes"""

    indicator = Spinner(speed=0.1)
    indicator.start() # prints 'animated' /|\ sequence in place
    fnct(*args, **kwargs)
    indicator.stop()


def dotItSlow(fnct, *args, **kwargs):
    """Displays progress dots (1 per sec) while the fnct executes"""

    indicator = Dotter(speed=1)
    indicator.start() # prints sequence of dots, 1 dot per second
    fnct(*args, **kwargs)
    indicator.stop()


def dotItFast(fnct, *args, **kwargs):
    """Displays progress dots (5 per sec) while the fnct executes"""

    indicator = Dotter(speed=0.2)
    indicator.start() # prints sequence of dots, 5 dots per second
    fnct(*args, **kwargs)
    indicator.stop()



if __name__=="__main__":

    poem = ['Mary had a little lamb,', 
            'Its fleece was white as snow.',
            'And everywhere that Mary went,',
            'The lamb was sure to go.',
            'It followed her to school one day,',
            'Which was against the rules.',
            'It made the children laugh and play,',
            'To see a lamb at school.']

    crunchingTime = 5.01
    msg = "Doing stuff for %s sec: " % crunchingTime
    print

    for line in poem:
        sys.stdout.write(msg)
        spinIt(time.sleep, crunchingTime)
        print line

    print

    for line in poem:
        sys.stdout.write(msg)
        dotItSlow(time.sleep, crunchingTime)
        print line

    print

    for line in poem:
        sys.stdout.write(msg)
        dotItFast(time.sleep, crunchingTime)
        print line
