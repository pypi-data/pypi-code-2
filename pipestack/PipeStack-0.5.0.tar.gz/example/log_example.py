"""
When you run this with the two logging lines present you'll see the log output:

::

    DEBUG:pipestack.app:Running the run() function <function terminator at 0xb75aa4fc>
    Here!
    DEBUG:pipestack.app:Need to leave these pipes: []

When you comment out these lines you'll get a warning:

::

    pipestack/app.py:141: UserWarning: The 'database' pipe does not have a logger set up
      'The %r pipe does not have a logger set up'%(name,)
    Here!
"""

#import logging
#logging.basicConfig(level=logging.DEBUG)

from pipestack.app import App, pipe
class SimpleApp(App):
    pipes = [
        pipe('database', 'pipestack.pipe:MarblePipe')
    ]

def terminator(bag):
    print "Here!"

app = SimpleApp()
app.start_flow(enter_pipes=['database'], terminator=terminator)

