from tw.api import Widget, JSLink, CSSLink, js_function
from tw.jquery import jquery_js

from datetime import datetime

__all__ = ["Epiclock"]

# declare your static resources here

dateformat_js = JSLink(modname=__name__,
               filename='static/jquery.dateformat.min.js', javascript=[jquery_js])
epiclock_js = JSLink(modname=__name__,
               filename='static/jquery.epiclock.min.js', javascript=[dateformat_js])

epiclock_css = CSSLink(modname=__name__, filename='static/jquery.epiclock.css')

class Epiclock(Widget):
    """ widget implementation
    """
    template = """<span id="${id}"></span>"""

    javascript = [epiclock_js]
    css = [epiclock_css]

    params = {
          # see included jquery.epiclock.js for more info
          "mode": "one of 'clock', 'explicit', 'countdown', 'countup', \
                    rollover', 'expire', 'loop', 'stopwatch', 'holdup', 'timer'",
          # see included jquery.dateformat.js for more info
          "format": "default is 'F j, Y g:i:s a'",
          "time": "javascript date to set the clock, eg : js_function('''new Date('Thu Jul 21 12:07:06 2010')'')",
          "server_time": "True or False, uses server time as a base for the clock",
          "offset": "change time, {'days':1} or {'hours':2} or {'minutes' : -20} for example",
          "utc": "normalize timezone, default to False (local time)",
          }
    #default values
    format = 'j-n-Y G:i:s'
    # display server time
    mode = 'explicit'
    time = None
    server_time = True
    offset = {}
    utc = False

    def __init__(self, id=None, parent=None, children=[], **kw):
        super(Epiclock, self).__init__(id, parent, children, **kw)

    def update_params(self, d):
        super(Epiclock, self).update_params(d)
        if not getattr(d,"id",None):
                raise ValueError, "Epiclock is supposed to have id"
        multi_params = dict(format=self.format,
                            mode=self.mode,
                            offset=self.offset,
                            utc=self.utc,
                            time=self.time,
                             )
        if self.server_time:
            multi_params['time'] = js_function("new Date('%s')" % datetime.now().ctime())
        call = js_function('$("#%s").epiclock' % d.id)(multi_params)
        self.add_call(call)