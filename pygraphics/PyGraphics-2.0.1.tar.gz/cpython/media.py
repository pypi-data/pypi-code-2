"""The media module. This contains global convenience functions
for manipulating PyGraphics objects, and imports all the supporting
modules fully.

Pictures currently support the following formats: JPEG, BMP, GIF, TIFF,
IM, MSP, PNG, PCX, and PPM.

Sounds support only uncompressed WAV files. For best quality use WAV files
with sampling rates of either 22050 or 44100. The default number of channels,
sampling rate, encoding, and buffering can be changed in the sound.py file."""

from picture import *
from sound import *
from color import *
import mediawindows as mw

mw.init_mediawindows()
picture.init_picture()
# init_sound()


####################----------------------------------------------------------
## Global Picture Functions
####################----------------------------------------------------------

def load_picture(filename):
    """Return a Picture object from filename filename."""

    return Picture(filename=filename)


def create_picture(w, h, col=white):
    """Return a Picture w pixels wide and h pixels high.
    Default Color col is white."""

    return Picture(w, h, col)


def crop_picture(pic, x1, y1, x2, y2):
    """Crop Picture pic so that only pixels inside the rectangular region
    with upper-left coordinates (x1, y1) and lower-right coordinates (x2, y2)
    remain.  The new upper-left coordinate is (0, 0)."""

    pic.crop(x1, y1, x2, y2)

# For backwards compatibility, including with the text.
crop = crop_picture

def get_pixel(pic, x, y):
    """Return the Pixel object at the coordinates (x, y) in Picture pic."""

    return pic.get_pixel(x, y)


def get_pixels(pic):
    """Return a list of Picture pic's Pixels from top to bottom,
    left to right."""

    return [pixel for pixel in pic]


def get_width(pic):
    """Return how many pixels wide Picture pic is."""

    return pic.get_width()


def get_height(pic):
    """Return how many pixels high Picture pic is."""

    return pic.get_height()


def show(pic):
    """Display Picture pic in separate window."""

    pic.show()


def show_external(pic):
    """Display Picture pic in an external application. The specific application
    depends on the operating system."""

    pic.show_external()


def update(pic):
    """Update Picture pic's display window."""

    pic.update()


def close(pic):
    """Close Picture pic's display."""

    pic.close()


def add_line(pic, x1, y1, x2, y2, col):
    """Draw a line of Color col from (x1, y1) to (x2, y2) on Picture pic."""

    pic.add_line(col, x1, y1, x2, y2)


def add_text(pic, x, y, s, col):
    """Draw str s in Color col on Picture pic starting at (x, y)."""

    pic.add_text(col, x, y, s)


def add_rect(pic, x, y, w, h, col):
    """Draw an empty rectangle of Color col, width w, and height h
    on Picture pic. The upper left corner of the rectangle is at (x, y)."""

    pic.add_rect(col, x, y, w, h)


def add_rect_filled(pic, x, y, w, h, col):
    """Draw a filled rectangle of Color col, width w, and height h
    on Picture pic. The upper left corner of the rectangle is at (x, y)."""

    pic.add_rect_filled(col, x, y, w, h)


def add_oval(pic, x, y, w, h, col):
    """Draw an empty oval of Color col, width w, and height h on Picture pic.
    The upper left corner of the oval is at (x, y)."""

    pic.add_oval(col, x, y, w, h)


def add_oval_filled(pic, x, y, w, h, col):
    """Draw a filled oval of Color col, width w, and height h on Picture pic.
    The upper left corner of the oval is at (x, y)."""

    pic.add_oval_filled(col, x, y, w, h)


def add_polygon(pic, point_list, col):
    """Draw an empty polygon of Color col with corners for every vertex
    in list point_list on Picture pic.

    Note:
    point_list is a list containing vertices xy coordinates
    (ex. [x1,y1,x2,y2,x3,y3]) It should contain at least
    three coordinate pairs."""

    pic.add_polygon(col, point_list)


def add_polygon_filled(pic, point_list, col):
    """Draw an empty polygon of Color col with corners for every vertex
    in list point_list on Picture pic.

    Note:
    point_list is a list containing vertices xy coordinates
    (ex. [x1,y1,x2,y2,x3,y3]) It should contain at least
    three coordinate pairs."""

    pic.add_polygon_filled(col, point_list)


####################----------------------------------------------------------
## Global Pixel Functions
####################----------------------------------------------------------


def set_red(pix, r):
    """Set the red value of Pixel pix to r."""

    pix.set_red(r)


def get_red(pix):
    """Return the red value of Pixel pix."""

    return pix.get_red()


def set_blue(pix, b):
    """Set the blue value of Pixel pix to b."""

    pix.set_blue(b)


def get_blue(pix):
    """Return the blue value of Pixel pix."""

    return pix.get_blue()


def set_green(pix, g):
    """Set the green value of Pixel pix to g."""

    pix.set_green(g)


def get_green(pix):
    """Return the green value of Pixel pix."""

    return pix.get_green()


def get_color(pix):
    """Return the Color object with Pixel pix's RGB values."""

    return pix.get_color()


def set_color(pix, col):
    """Set the RGB values of Pixel pix to those of Color col."""

    pix.set_color(col)


def get_x(pix):
    """Return the x coordinate of Pixel pix."""

    return pix.get_x()


def get_y(pix):
    """Return the y coordinate of Pixel pix."""

    return pix.get_y()


####################----------------------------------------------------------
## Global Color Functions
####################----------------------------------------------------------


def distance(col1, col2):
    """Return the Euclidean distance between the RGB values of Color col1 and
    Color col2."""

    return col1.distance(col2)


def darken(col):
    """Darken Color col by 35%."""

    col.make_darker()


def lighten(col):
    """Lighten Color col by 35%."""

    col.make_lighter()


def create_color(r, g, b):
    """Return a Color object with RGB values r, g, and b."""

    return Color(r, g, b)


####################----------------------------------------------------------
## Global Sound Functions
####################----------------------------------------------------------


def load_sound(filename):
    """Return the Sound at file filename. Requires: file is an uncompressed
    .wav file."""

    return Sound(filename=filename)


def create_sound(samp):
    """Return a silent Sound samp samples long."""

    return Sound(samples=samp)


def create_note(note, samp, octave=0):
    """Return a Sound samp samples long with the frequency according to
    str note. The following are acceptable arguments for note, starting
    at middle C:

    'C', 'D', 'E', 'F', 'G', 'A', and 'B'

    To raise or lower an octave specify the argument octave as a
    positive or negative int. Positive to raise by that many octaves
    and negative to lower by that many."""

    return Note(note, samp, octave=octave)


def get_samples(snd):
    """Return a list of Samples in Sound snd."""

    return [samp for samp in snd]


def get_max_sample(snd):
    """Return Sound snd's highest sample value. If snd is stereo
    return the absolute highest for both channels."""

    snd.get_max()


def get_min_sample(snd):
    """Return Sound snd's lowest sample value. If snd is stereo
    return the absolute lowest for both channels."""

    snd.get_min()


def concatenate(snd1, snd2):
    """Return a new Sound object with Sound snd1 followed by Sound snd2."""

    return snd1 + snd2


def append_silence(snd, samp):
    """Append samp samples of silence onto Sound snd."""

    snd.append_silence(samp)


def crop_sound(snd, first, last):
    """Crop snd Sound so that all Samples before int first and
    after int last are removed. Cannot crop to a single sample.
    Negative indices are supported."""

    snd.crop(first, last)


def insert(snd1, snd2, i):
    """Insert Sound snd2 in Sound snd1 at index i."""

    snd1.insert(snd2, i)


def play(snd):
    """Play Sound snd from beginning to end."""

    snd.play()


def play_in_range(snd, first, last):
    """Play Sound snd from index first to last."""

    snd.play(first, last)


def stop(snd):
    """Stop playing Sound snd."""

    snd.stop()


def get_sampling_rate(snd):
    """Return the Sound snd's sampling rate."""

    return snd.get_sampling_rate()


def get_sample(snd, i):
    """Return Sound snd's Sample object at index i."""

    return snd.get_sample(i)


def get_waveform(snd, first=0, last=-1, width=1250, height=128,
        theme='DEFAULT'):
    """Return a Picture width pixels wide and height pixels high
    of the waveform graph of Sound snd from index first to last.
    Use the color scheme denoted by the str theme. Available arguments
    are 'DEFAULT', 'PRO', 'OCEAN', 'NOTEBOOK', 'HEART'."""

    snd_copy = snd.copy()
    snd_copy.crop(first, last)
    return snd_copy.get_waveform_graph(len(snd_copy) / 12500, width, height,
        theme)


def get_spectrogram(snd, width=1024, height=300):
    """Unimplemented"""

    pass


def get_spectrum(snd, width=1024, height=300):
    """Unimplemented"""

    pass


####################----------------------------------------------------------
## Global Sample Functions
####################----------------------------------------------------------

def get_index(samp):
    """Return Sample samp's index."""

    return samp.get_index()


def set_value(mono_samp, v):
    """Set MonoSample mono_samp's value to v."""

    mono_samp.set_value(v)


def get_value(mono_samp):
    """Return MonoSample mono_samp's value."""

    return mono_samp.get_value()


def set_values(stereo_samp, left, right):
    """Set StereoSample stereo_samp's left value to left and
    right value to right."""

    stereo_samp.set_values(left, right)


def get_values(stereo_samp):
    """Return StereoSample stereo_samp's values in a tuple, (left, right)."""

    return stereo_samp.get_values()


def set_left(stereo_samp, v):
    """Set StereoSample stereo_samp's left value to v."""

    stereo_samp.set_left(v)


def get_left(stereo_samp):
    """Return StereoSample stereo_samp's left value."""

    return stereo_samp.get_left()


def set_right(stereo_samp, v):
    """Set StereoSample stereo_samp's right value to v."""

    stereo_samp.set_right(v)


def get_right(stereo_samp):
    """Return StereoSample stereo_samp's right value."""

    return stereo_samp.get_right()


####################----------------------------------------------------------
## Global Media Object Functions
####################----------------------------------------------------------


def save_as(obj, filename=None):
    """Prompt user to pick a directory and filename then write media.py object
    obj to that filename. Requires that file format is specified in filename
    by extensions."""

    if not filename:
        filename = choose_save_filename()

    if filename:
        obj.save_as(filename)


def save(obj):
    """Write media.py object obj back to its previous file."""

    if obj.get_filename() == '':
        save_as(obj)
    else:
        obj.save()


def inspect(obj):
    """Inspect object obj. Works on Sound and Picture objects."""

    obj.inspect()


def close_inspect(obj):
    """Close an open inspector window for object obj. Works on Sound and
    Picture objects."""

    obj.close_inspect()


def copy(obj):
    """Return a deep copy of object obj. Works on Color, Sound, and Picture
    objects."""

    return obj.copy()


####################----------------------------------------------------------
## Dialogs
####################----------------------------------------------------------

def choose_save_filename():
    """Prompt user to pick a directory and filename. Return the path
    to the new file."""

    return mw.choose_save_filename()


def choose_file():
    """Prompt user to pick a file. Return the path to that file."""

    return mw.choose_file()


def choose_folder():
    """Prompt user to pick a folder. Return the path to that folder."""

    return mw.choose_folder()


def choose_color():
    """Prompt user to pick a color. Return a RGB Color object."""

    return mw.choose_color()

####################----------------------------------------------------------
## Other GUI Shenanigans
####################----------------------------------------------------------

def say(text):
    """Display text to the user in a GUI window."""
    return mw.say(text)

if __name__ == "__main__":
    pic = create_picture(300, 400, lightgrey)
    pic.inspect()