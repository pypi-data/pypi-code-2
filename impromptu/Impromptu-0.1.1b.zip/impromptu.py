#!/usr/bin/env python
"""Show scrolling text read from the HTML file given on the command line."""

HELP_TEXT = """\
<blockquote><pre>
<font face="Georgia" size="4">
<tt>F1      </tt> = Open / Close help screen
<tt>F11     </tt> = Toggle fullscreen mode (use <tt>Command-F</tt> on OS X)
<tt>ESCAPE  </tt> = Close window and exit / Close help screen
<tt>SPACE   </tt> = Pause / Resume scrolling
<tt>CONTROL </tt> = Pause scrolling momentarily (release key to resume)
<tt>RETURN  </tt> = Set scrolling speed to default
<tt>UP      </tt> = Increase scrolling speed (max. 250 pixels/second)
<tt>DOWN    </tt> = Decrease scrolling speed (min. 1 pixel/second)
<tt>RIGHT   </tt> = Change scrolling direction to up-/forwards
<tt>LEFT    </tt> = Change scrolling direction to down-/backwards
<tt>PAGEUP  </tt> = Scroll back one screen
<tt>PAGEDOWN</tt> = Scroll forward one screen
<tt>HOME    </tt> = Jump to start
<tt>END     </tt> = Jump to end
<tt>+       </tt> = Increase font size (max. 100 points)
<tt>-       </tt> = Decrease font size (min. 6 points)
<tt>0       </tt> = Set font size to default
<tt>R       </tt> = Show display framerate
</font>
</pre></blockquote>
"""

__author__      = 'Christopher Arndt'
__license__     = 'MIT license'
__version__     = '$Id: impromptu.py 477 2011-01-21 11:55:56Z carndt $'
__usage__       = '%prog [OPTIONS] FILENAME'

# standard library modules
import optparse
import os
import sys

# third-party packages
import pyglet
import pyglet.font

from pyglet.font import load as load_font
from pyglet.text.layout import ScrollableTextLayout
from pyglet.text.formats.html import HTMLDecoder
from pyglet.window import key


# global constants
DEFAULT_SPEED = 20
MAX_SPEED = 250
MAX_UPDATE_INTERVAL = 50
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDING_X = 20
PADDING_Y = 5
DEFAULT_FONT_LIST= 'Georgia'
DEFAULT_FONT_SIZE = 32
LINE_SPACING = 1.9


# utility functions
def load_html(filename):
    if filename == "-":
        f = sys.stdin
    else:
        f = open(filename)
    html = f.read()
    if f is not sys.stdin:
        f.close()
    return html

def parse_html(html, font_name=None, font_size=12, line_spacing=1.6):
    """Load HTML from given filename, parse it and return document instance."""
    decoder = HTMLDecoder()
    decoder.default_style['font_name'] = font_name
    decoder.default_style['font_size'] = font_size
    decoder.default_style['line_spacing'] = int(font_size * line_spacing)

    location = pyglet.resource.FileLocation(os.path.dirname(__file__))
    document = decoder.decode(html, location)
    return document

def list_screens():
    """Print a list of all available screens."""
    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    for i, screen in enumerate(display.get_screens()):
        print "%i: %s" % (i+1, screen)

# display element classes
class DynamicTextDisplay(object):
    """Display a label dynamically updating its text on the main window.

    Public attributes:

        `label` : `pyglet.font.Text`
            The label which is displayed.

    This is a generalisation of pyglet.clock.ClockDisplay.

    """

    def __init__(self, window, text, show=True, clock=None, interval=0.25,
            font_name=None, font_size=28, format='%(text)s', x=10, y=10,
            color=(196, 196, 196, 20), halign='left', valign='baseline'):
        """Create a SpeedDisplay.

        All parameters are optional.  By default, a large translucent
        font will be used to display the speed as an integer.

        :Parameters:
            `font` : `pyglet.font.Font`
                The font to format text in.
            `interval` : float
                The number of seconds between updating the display.
            `format` : str
                A format string describing the format of the text.  This
                string is modulated with the dict ``{'fps' : fps}``.
            `color` : 4-tuple of float
                The color, including alpha, passed to ``glColor4f``.
            `clock` : `Clock`
                The clock which determines the time.  If None, the default
                clock is used.

        """

        self.window = window
        if isinstance(text, basestring):
            self._update_func = lambda: {'text:': text}
        elif callable(text):
            self._update_func = text
        else:
            raise TypeError("'text' must be callable or string.")

        if not font_name:
            font_name = ('Helvetica', 'Arial', None)
        font = pyglet.font.load(font_name, font_size, bold=True)

        self.format = format
        label_text = format % self._update_func()
        self.label = pyglet.font.Text(font, label_text, color=color, x=x, y=y,
                                      halign=halign, valign=valign)

        if clock is None:
            clock = pyglet.clock
        self.clock = clock
        self.interval = interval
        if show:
            self.show()

    def show(self, time=None):
        """Schedule update function."""
        # This might still be scheduled from an earlier call to 'show()'
        self.clock.unschedule(self.hide)
        # schedule update function
        self.clock.unschedule(self.update_text)
        self.clock.schedule_interval(self.update_text, self.interval)
        if time:
            # if 'time' is non-null, schedule call to 'hide()' in 'time' sec.
            self.clock.schedule_once(self.hide, time)
        self._visible = True

    def hide(self, dt=0):
        """Remove the display from its clock's schedule.

        `DynamicTextDisplay` uses `pyglet.clock.schedule_interval` to
        periodically update its display label. Even if the DynamicTextDisplay
        is not being used at the moment, its update method will still be
        scheduled, which can be a resource drain.  Call this method to
        unschedule the update method and allow the DynamicTextDisplay to be
        garbage collected.

        """
        self._visible = False
        self.clock.unschedule(self.update_text)

    def toggle(self):
        if not getattr(self, '_visible', False):
            self.show()
        else:
            self.hide()

    def update_text(self, dt=0):
        """Scheduled method to update the label text."""
        self.label.text = self.format % self._update_func()

    def draw(self):
        """Method called each frame to render the label."""
        if getattr(self, '_visible', False):
            self.label.draw()


class ScrollingTextWindow(pyglet.window.Window):
    """Displays a HTML document and scrolls the text automatically."""

    def __init__(self, text, default_speed=DEFAULT_SPEED, screen=None,
                fullscreen=False, font_name=None, font_size=DEFAULT_FONT_SIZE):
        super(ScrollingTextWindow, self).__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
            screen=screen, resizable=True)
        self.set_minimum_size(300, 200)
        self.set_caption("Impromptu")

        self._font_size = font_size
        self.line_spacing = LINE_SPACING
        self.document = parse_html(
            text, font_name=font_name, font_size=font_size,
            line_spacing=self.line_spacing)
        self.scrollarea = ScrollableTextLayout(self.document,
            width=self.width - PADDING_X * 2,
            height=self.height - PADDING_Y * 2,
            multiline=True)
        self.scrollarea.anchor_y = 'top'

        # 'up' or 'down'
        self.direction = 'up'
        self.paused = False

        # in pixels per second
        self.speed = self.default_speed = default_speed
        self.speed_display = DynamicTextDisplay(self,
            lambda: {'speed': self.speed}, show=False,
            format='Speed: %(speed)i px/s', interval=0.03,
            x=self.width-PADDING_X, halign='right')

        # Framerate display
        self.fps_display = DynamicTextDisplay(self,
            lambda: {'fps': pyglet.clock.get_fps()}, show=False,
            format='FPS: %(fps).2f')

        if fullscreen:
            self.toggle_fullscreen()

    def show_help(self):
        self.scrollarea.document = parse_html(HELP_TEXT, "serif", 18)
        self._saved_state = {
            'view_y': self.scrollarea.view_y,
            'paused': self.paused,
        }
        self.paused = True
        self.scrollarea.view_y = 0
        self._help_active = True

    def close_help(self):
        self.scrollarea.document = self.document
        self.scrollarea.view_y = self._saved_state['view_y']
        self.paused = self._saved_state['paused']
        self._help_active = False

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)
        self.set_exclusive_keyboard(self.fullscreen)
        self.set_mouse_visible(not self.fullscreen)

    def scroll_text(self, dt):
        if not self.paused:
            increment = dt / (1.0 / self.speed)
            if self.direction == 'up':
                self.scrollarea.view_y -= increment
            elif self.direction == 'down':
                self.scrollarea.view_y += increment

    def scroll_to_start(self):
        self.scrollarea.view_y = 0

    def scroll_to_end(self):
        self.scrollarea.view_y = (self.scrollarea.height -
                                  self.scrollarea.content_height)

    def set_speed(self, speed=None):
        if speed is None:
            speed = self.default_speed
        else:
            speed = max(1, min(speed, MAX_SPEED))
        self.speed = speed
        self.speed_display.show(1)

    def increase_speed(self, amount=1):
        self.speed = min(self.speed + amount, MAX_SPEED)
        self.speed_display.show(1)

    def decrease_speed(self, amount=1):
        self.speed = max(self.speed - amount, 1)
        self.speed_display.show(1)

    def _get_speed(self):
        return getattr(self, '_speed', 0)

    def _set_speed(self, speed):
        if speed != getattr(self, '_speed', None):
            self._speed = speed
            update_interval = min(MAX_UPDATE_INTERVAL, 1.0/self._speed)
            pyglet.clock.unschedule(self.scroll_text)
            pyglet.clock.schedule_interval(self.scroll_text, update_interval)
    speed = property(_get_speed, _set_speed)

    def increase_font_size(self, amount=1):
        self.font_size = min(self.font_size + amount, 100)

    def decrease_font_size(self, amount=1):
        self.font_size = max(self.font_size - amount, 6)

    def _get_font_size(self):
        return self._font_size

    def _set_font_size(self, font_size):
        if font_size != self._font_size:
            self.document.set_style(0, len(self.document.text),
                {'font_size': font_size,
                 'line_spacing': int(font_size * self.line_spacing)}
            )
            self._font_size = font_size
    font_size = property(_get_font_size, _set_font_size)

# event handlers
class EventHandlers(object):
    def __init__(self, window):
        self.w = window

    def on_resize(self, width, height):
        # Wrap text to the width of the window
        self.w.scrollarea.width = self.w.width - PADDING_X * 2
        self.w.scrollarea.height = self.w.height - PADDING_Y * 2
        self.w.scrollarea.x = PADDING_X
        self.w.scrollarea.y = self.w.height - PADDING_Y
        self.w.speed_display.label.x = self.w.width - PADDING_X

    def on_draw(self):
        self.w.clear()
        self.w.scrollarea.draw()
        self.w.fps_display.draw()
        self.w.speed_display.draw()

    def on_key_press(self, symbol, modifiers):
        if getattr(self.w, '_help_active', False):
            if symbol in (key.ESCAPE, key.F1):
                self.w.close_help()
                return True
            return

        if sys.platform == 'darwin':
            if symbol == key.F and modifiers & key.MOD_COMMAND:
                self.w.toggle_fullscreen()
        else:
            if symbol == key.F11:
                self.w.toggle_fullscreen()

        if symbol in (key.F1, key.H):
            self.w.show_help()
        elif symbol == key.RETURN:
            self.w.set_speed(None)
        elif symbol == key.SPACE:
            self.w.paused = not self.w.paused
        elif symbol in (key.LCTRL, key.RCTRL):
            self.w.paused = True
        elif symbol == key.R:
            self.w.fps_display.toggle()
        elif symbol == key._0:
            self.w.font_size = DEFAULT_FONT_SIZE
        elif symbol == key.RIGHT:
            self.w.direction = 'up'
        elif symbol == key.LEFT:
            self.w.direction = 'down'
        elif symbol == key.HOME:
            self.w.scroll_to_start()
        elif symbol == key.END:
            self.w.scroll_to_end()
        elif symbol == key.Q:
            pyglet.app.exit()
        elif symbol in (key.PLUS, key.NUM_ADD):
            self.w.increase_font_size()
        elif symbol in (key.MINUS, key.NUM_SUBTRACT):
            self.w.decrease_font_size()

    #def on_text(self, text):
    #    pass

    def on_text_motion(self, motion):
        if motion == key.MOTION_UP:
            self.w.increase_speed()
        elif motion == key.MOTION_DOWN:
            self.w.decrease_speed()
        elif motion == key.MOTION_PREVIOUS_PAGE:
            self.w.scrollarea.view_y += self.w.scrollarea.height
        elif motion == key.MOTION_NEXT_PAGE:
            self.w.scrollarea.view_y -= self.w.scrollarea.height

    def on_key_release(self, symbol, modifiers):
        if symbol in (key.LCTRL, key.RCTRL):
            self.w.paused = False

# main script entry point
def main(args):

    optparser = optparse.OptionParser(usage=__usage__,
        description=__doc__.splitlines()[0])
    optparser.add_option('-f', '--font-name',
        metavar="FONT", dest="font_name", default=DEFAULT_FONT_LIST,
        help="Default font for normal text.")
    optparser.add_option('-s', '--font-size', type="int",
        metavar="SIZE", dest="font_size", default=DEFAULT_FONT_SIZE,
        help="Default font size in points for normal text.")
    optparser.add_option('-S', '--speed', type="int",
        metavar="SPEED", dest="speed", default=DEFAULT_SPEED,
        help="Scrolling speed in pixels per second (default: %i)." %
        DEFAULT_SPEED)
    optparser.add_option('-F', '--fullscreen',
        action="store_true", dest="fullscreen",
        help="Start in full screen mode (press F11 to toggle).")
    optparser.add_option('-d', '--screen', type="int",
        metavar="SCREEN", dest="screen",
        help="Number of the display screen to use.")
    optparser.add_option('-l', '--list-screens',
        action="store_true", dest="list_screens",
        help="List available display screens.")

    if args is None:
        options, args = optparser.parse_args(args)
    else:
        options, args = optparser.parse_args()

    if options.list_screens:
        list_screens()
    else:
        if args:
            filename = args[0]
        else:
            print "Reading from standard input. Ctrl-C to abort."
            filename = '-'

        if options.screen:
            platform = pyglet.window.get_platform()
            display = platform.get_default_display()
            try:
                screen = display.get_screens()[options.screen-1]
            except:
                print "Error: Screen no. %i not available" % options.screen
                print "Use option '-l' to get a list of available screens."
                return 1
        else:
            screen = None

        try:
            html = load_html(filename)
        except (IOError, OSError) as exc:
            print "Could not read '%s': %s" % (filename, exc)
            return 1
        except KeyboardInterrupt:
            return 0

        window = ScrollingTextWindow(html, options.speed, screen=screen,
            fullscreen=options.fullscreen, font_name=options.font_name,
            font_size=options.font_size)
        window.push_handlers(EventHandlers(window))

        pyglet.gl.glClearColor(1, 1, 1, 1)

        try:
            pyglet.app.run()
        except KeyboardInterrupt:
            pass

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] ))
