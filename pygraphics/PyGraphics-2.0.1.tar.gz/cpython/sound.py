'''The Sound class and helper functions. This currently supports only 
uncompressed .wav files. For best quality use .wav files with sampling
rates of either 22050 or 44100. The default number of channels,
sampling rate, encoding, and buffering can be changed in the sound.py
file.'''

import sample
import picture
import mediawindows as mw
import Image
import math
import numpy
import pygame
import wave
import sndhdr
import os

####################------------------------------------------------------------
## Defaults and Globals
####################------------------------------------------------------------

GRAPH_COLOR_THEMES = {'NOTEBOOK' : ((229, 225, 193), (34, 13, 13)),
                      'OCEAN' : ((0, 64, 128), (255, 255, 255)),
                      'HEART' : ((0, 0, 0), (0, 255, 0)),
                      'DEFAULT' : ((255, 255, 255), (0, 0, 0)),
                      'PRO' : ((0, 0, 0), (255, 255, 255))}
SOUND_FORMATS = ['.wav']
DEFAULT_SAMP_RATE = None
DEFAULT_ENCODING = None
DEFAULT_CHANNELS = None
DEFAULT_BUFFERING = None
SND_INITIALIZED = False
AUDIO_ENCODINGS = { 8 : numpy.uint8,   # unsigned 8-bit
     16 : numpy.uint16, # unsigned 16-bit
     -8 : numpy.int8,   # signed 8-bit
     -16 : numpy.int16  # signed 16-bit
     }

####################------------------------------------------------------------
## Initializer
####################------------------------------------------------------------

def init_sound(samp_rate=22050, encoding=-16, channels=1): 
    '''Initialize this module. Must be done before any sounds are created.
    
    WARNING: If used with picture.py, it must be initialized after initializing
    picture.py.'''
    
    global SND_INITIALIZED, DEFAULT_SAMP_RATE, DEFAULT_ENCODING, \
    DEFAULT_CHANNELS, DEFAULT_BUFFERING
            
    if not SND_INITIALIZED:
        if not mw._THREAD_RUNNING:
            mw.init_mediawindows()
        DEFAULT_SAMP_RATE = samp_rate
        DEFAULT_ENCODING = encoding
        DEFAULT_CHANNELS = channels
        DEFAULT_BUFFERING = 3072
        pygame.mixer.pre_init(DEFAULT_SAMP_RATE, 
                              DEFAULT_ENCODING, 
                              DEFAULT_CHANNELS, 
                              DEFAULT_BUFFERING)
        #Dan - removed mw.thread_exec(
        # This breaks media.choose_file() on some platforms -- not real fix 
        pygame.mixer.init()
        SND_INITIALIZED = True
    else:
        raise Exception('Sound has already been initialized!')

####################------------------------------------------------------------
## Sound class
####################------------------------------------------------------------


class Sound(object):
    '''A Sound class as a wrapper for the pygame.mixer.Sound object.'''
        
    def __init__(self, filename=None, samples=None, seconds=None, sound=None):
        '''Create a Sound.
                
        Requires one of:
        - named str argument filename (with .wav extension), 
                e.g. Sound(filename='sound.wav')
        - named int argument samples, e.g. Sound(samples=2000)
        - named int argument seconds, e.g. Sound(seconds=10) 
        - named pygame.mixer.Sound argument sound, 
                e.g. Sound(sound=pygame.mixer.Sound)
        
        Filename takes precedence over samples, which take precedence 
        over seconds, which in turn takes precedence over sound.'''
        
        if not SND_INITIALIZED:
            raise Exception('Sound is not initialized. Run init_sound() first.')
        
        self.channels = DEFAULT_CHANNELS
        self.samp_rate = DEFAULT_SAMP_RATE
        self.numpy_encoding = AUDIO_ENCODINGS[DEFAULT_ENCODING]
        self.encoding = DEFAULT_ENCODING
        self.inspectpic = None
        self.set_filename(filename)
        
        if filename != None:
            snd = load_pygame_sound(filename)
            
        elif samples != None:
            snd = create_pygame_sound(samples)
            
        elif seconds != None:
            samples = int(seconds * self.samp_rate)
            snd = create_pygame_sound(samples)
            
        elif sound != None:
            snd = sound
            
        else:
            raise TypeError("No arguments were given to the Sound constructor.")
                    
        self.set_pygame_sound(snd)
            
    def __eq__ (self, snd):
        if self.get_channels() == 1 and snd.get_channels() == 1:
            return numpy.all (self.samples == snd.samples)
        elif self.get_channels() == 2 and snd.get_channels() == 2:
            return numpy.all (self.samples == snd.samples)
        else:
            raise ValueError('Sound snd must have same number of channels.')
        
    def __str__(self):
        '''Return the number of Samples in this Sound as a str.'''
        
        return "Sound of length " + str(len(self))

    def __iter__(self):
        '''Return this Sound's Samples from start to finish.'''
        
        l = len(self)
        
        if self.channels == 1:
            for i in range(l):
                yield sample.MonoSample(self.samples, i)
        elif self.channels == 2:
            for i in range(l):
                yield sample.StereoSample(self.samples, i)
  
    def __len__(self):
        '''Return the number of Samples in this Sound.'''
        
        return len(self.samples)

    def __add__(self, snd):
        '''Return a Sound object with this Sound followed by Sound snd.'''
        
        new = self.copy()
        new.append(snd)
        return new

    def __mul__(self, num):
        '''Return a Sound object with this Sound repeated num times.'''
        
        new = self.copy()
        l = int(num) - 1
        
        for time in range(l):
            new.append(self)
        return new

    def set_pygame_sound(self, pygame_snd):
        '''Set this Sound's pygame Sound object.'''
        
        self.pygame_sound = pygame_snd
        
        # self.samples is a numpy array object (either 1D or 2D depending on the
        # number of channels). This object allows access to specific samples
        # in the buffer.
        self.samples = pygame_to_sample_array(pygame_snd)
        self.player = None
        
    def get_pygame_sound(self):
        '''Return this Sound's pygame Sound object.'''
        
        return self.pygame_sound

    def copy(self):
        '''Return a deep copy of this Sound.'''
        
        samples = self.samples.copy()
        new_pygame_snd =  sample_array_to_pygame(samples)
        return Sound(sound=new_pygame_snd)

    def append_silence(self, s):
        '''Append s samples of silence to each of this Sound's channels.'''
        
        if self.channels == 1:
            silence_array = numpy.zeros(s, self.numpy_encoding)
        else:
            silence_array = numpy.zeros((s, 2), self.numpy_encoding)
        pygame_silence =  sample_array_to_pygame(silence_array)
        self.append(Sound(sound=pygame_silence))

    def append(self, snd):
        '''Append Sound snd to this Sound. Requires that snd has same number of
        channels as this Sound.'''
        
        if self.get_channels() == snd.get_channels():
            snd_samples = pygame_to_sample_array(snd.get_pygame_sound())
            my_samples = self.samples
            new_samples = numpy.concatenate((my_samples, snd_samples))
            self.set_pygame_sound(sample_array_to_pygame(new_samples))
        else:
            raise ValueError('Sound snd must have same number of channels.')
    
    def insert(self, snd, i):
        '''Insert Sound snd at index i. Requires that snd has same number of
        channels as this Sound. Negative indices are supported.'''

        if self.get_channels() == snd.get_channels() == 1:
            first_chunk = self.samples[:i]
            second_chunk = self.samples[i:]
            new_samples = numpy.concatenate((first_chunk, 
                                             snd.samples, 
                                             second_chunk))
            self.set_pygame_sound(sample_array_to_pygame(new_samples))
        elif self.get_channels() == snd.get_channels() == 2:
            first_chunk = self.samples[:i, :]
            second_chunk = self.samples[i:, :]
            new_samples = numpy.vstack((first_chunk, 
                                        snd.samples, 
                                        second_chunk))
            
            self.set_pygame_sound(sample_array_to_pygame(new_samples))
        else:
            raise ValueError("Sound snd must have same number of channels.")

    def crop(self, first, last):
        '''Crop this Sound so that all Samples before int first and 
        after int last are removed. Cannot crop to a single sample. 
        Negative indices are supported'''

        first = first % len(self)
        last = last % len(self)
        
        new_samples = self.samples[first:last + 1]
        self.set_pygame_sound(sample_array_to_pygame(new_samples))

    def normalize(self):
        '''Maximize the amplitude of this Sound's wave. This will increase
        the volume of the Sound.'''
        
        maximum = self.samples.max()
        minimum = self.samples.min()
        factor = min(32767.0/maximum, 32767.0/abs(minimum))        
        self.samples *= factor        
    
    def close_inspect(self):
        '''Close the Inspector window.'''
        
        if self.inspectpic and not self.inspectpic.is_closed():
            self.inspectpic.close()
            self.inspectpic = None
        elif self.inspectpic.is_closed():
            self.inspectpic = None
        else:
            pass # Error?
    
    def inspect(self, first=0, last=-1, theme='DEFAULT'):
        '''Make and display this Sound's waveform graph from index first 
        to last. If the Sound is already displayed updated it's open
        Picture.'''
        
        chunk = self.copy()
        chunk.crop(first, last)
        if self.inspectpic and not self.inspectpic.is_closed():
            graph = chunk.get_waveform_image(len(chunk) / 12500, theme=theme)
            graph = graph.resize((1250, 128), Image.ANTIALIAS)
            self.inspectpic.set_image(graph)
            self.inspectpic.update()
        else:
            self.inspectpic = chunk.get_waveform_graph(len(chunk) / 12500, x=1250, y=128, theme=theme)
            self.inspectpic.show()
         
    def get_waveform_graph(self, s_per_pixel, x=None, y=None, theme='DEFAULT'):
        '''Return a Picture object with this Sound's waveform point graph
        with s_per_pixel samples per pixel. If specified the picture will
        be resized to x pixels wide and y pixels high. This works best 
        with sounds in a 16 signed bits encoding.
        
        WARNING: 
        This can take very long if too many samples per pixel 
        are asked for.
        
        RECOMMENDED ARGUMENTS: 
        somesound.get_waveform_graph(len(somesound) / 12500, x=1250, y=128)'''
    
        graph = self.get_waveform_image(s_per_pixel, theme=theme)
        if x and y:
            graph = graph.resize((x, y), Image.ANTIALIAS)
        return picture.Picture(image=graph)
    
    def get_waveform_image(self, s_per_pixel, v_per_pixel=128, theme="DEFAULT"):
        '''Return a PIL Image object with this Sound's waveform point graph
        with s_per_pixel samples per pixel and v_per_pixel values per pixel. 
        
        NOTE: 
        Sounds encoded in 16 bits have a possible range of values from
        -32768 to 32767. This is a range of about 65536. Therefore to have 
        a graph of 512 pixels high a v_per_pixel of 128 is needed as default.
        
        WARNING: 
        This method can take very long if too many samples per pixel 
        are asked for.'''
        
        if v_per_pixel < 1:
            v_per_pixel = 1
        if s_per_pixel < 1:
            s_per_pixel = 1

        # This width is the length of the sound divided by the number
        # of samples per pixel. 2 pixels are added for padding.    
        width = int(len(self) / s_per_pixel) + 2

        # This height is absolute size of the possible range of sound
        # samples divided by the number of values per pixel. 2 pixels
        # are added for padding and accounted for in the calculations
        height = int(65536 / v_per_pixel) + 2
        graph = Image.new("RGB", (width, height), GRAPH_COLOR_THEMES[theme][0])
        
        pixels = graph.load()
        i = 1
        sample_i = 0
        while i < width - 1:
            
            # This is the zero line
            pixels[i, int(32768 / v_per_pixel) + 1] = GRAPH_COLOR_THEMES[theme][1]
            
            # Get the value and calculate it's appropriate y coordinate
            val = self.samples[sample_i, 0]
            y_coord = int((val + 32768) / v_per_pixel) + 1
            _draw_dot(pixels, i, y_coord, GRAPH_COLOR_THEMES[theme][1])    
            i += 1
            sample_i += s_per_pixel
                    
        return graph

    def play(self, first=0, last=-1):
        '''Play this Sound from sample index first to last. As default play
        the entire Sound.'''
        
        self.player = self.copy()
        self.player.crop(first, last)
        self.player.get_pygame_sound().play()

    def stop(self):
        '''Stop playing this Sound.'''
        
        if self.player:
            self.player.get_pygame_sound().stop()

    def get_sampling_rate(self):
        '''Return the number of Samples this Sound plays per second.'''

        return self.samp_rate

    def get_sample(self, i):
        '''Return this Sound's Sample object at index i. Negative indices are
        supported.'''

        if self.channels == 1:
            return sample.MonoSample(self.samples, i)
        elif self.channels == 2:
            return sample.StereoSample(self.samples, i)
    
    def get_max(self):
        '''Return this Sound's highest sample value. If this Sound is stereo
        return the absolute highest for both channels.'''
        
        return self.samples.max()
        
    def get_min(self):
        '''Return this Sound's lowest sample value. If this Sound is stereo
        return the absolute lowest for both channels.'''
        
        return self.samples.min()

    def get_channels(self):
        '''Return the number of channels in this Sound.'''
        
        return self.channels

    def set_filename(self, filename=None):
        '''Set this Sound's filename to filename. If filename is None 
        set this Sound's filename to the empty string.'''
        
        if filename != None:
            self.filename = filename
        else:
            self.filename = ''
    
    def get_filename(self):
        '''Return this Sound's filename.'''

        return self.filename
         
    def save_as(self, filename):
        '''Save this Sound to filename filename and set its filename.'''
        
        ext = os.path.splitext(filename)[-1]
        if ext in SOUND_FORMATS or ext in [e.upper() for e in SOUND_FORMATS]:
            self.set_filename(filename=filename)
            wav = wave.open(filename, 'w')
            wav.setnchannels(self.get_channels())
            
            # calculate the number of bytes for this sound
            fmtbytes = (abs(self.encoding) & 0xff) >> 3
            wav.setsampwidth(fmtbytes)
            
            wav.setframerate(self.get_sampling_rate())
            wav.setnframes(len(self))
            wav.writeframes(self.pygame_sound.get_buffer().raw)
            wav.close()
        else:
            raise ValueError("%s is not one of the supported file formats." \
                             % ext)        
        
    def save(self):
        '''Save this Sound to its filename. If an extension is not specified
        the default is .wav.'''
 
        filename = os.path.splitext(self.get_filename())[0]
        ext = os.path.splitext(self.get_filename())[-1]
        if ext == '':
            self.save_as(filename + '.wav')
        else:
            self.save_as(self.get_filename())
        
        
####################------------------------------------------------------------
## Note class
####################------------------------------------------------------------


class Note(Sound):
    '''A Note class to create different notes of the C scale. Inherits from Sound,
    does everything Sounds do, and can be combined with Sounds.'''
    
    # These are in Hz. 
    frequencies = {'C' : 261.63,
                   'D' : 293.66,
                   'E' : 329.63,
                   'F' : 349.23,
                   'G' : 392,
                   'A' : 440,
                   'B' : 493.88}
    
    default_amp = 6000
    
    def __init__(self, note, s, octave=0):
        '''Create a Note s samples long with the frequency according to 
        str note. The following are acceptable arguments for note, starting 
        at middle C:
            
        'C', 'D', 'E', 'F', 'G', 'A', and 'B'
            
        To raise or lower an octave specify the argument octave as a
        positive or negative int. Positive to raise by that many octaves
        and negative to lower by that many.'''

        
        if not SND_INITIALIZED:
            raise Exception('Sound is not initialized. Run init_sound() first.')
        
        self.channels = DEFAULT_CHANNELS
        self.samp_rate = DEFAULT_SAMP_RATE
        self.numpy_encoding = AUDIO_ENCODINGS[DEFAULT_ENCODING]
        self.encoding = DEFAULT_ENCODING
        self.inspectpic = None
        self.set_filename(None)

        if octave < 0: 
            freq = self.frequencies[note] / (2 ** abs(octave))
        elif octave > 0:
            freq = self.frequencies[note] * (2 ** octave)
        else:
            freq = self.frequencies[note]
        
        snd = create_sine_wave(int(freq), self.default_amp, s)
        self.set_pygame_sound(snd)
                
        
####################------------------------------------------------------------
## Helper functions
####################------------------------------------------------------------


def load_pygame_sound(filepath):
    '''Return a pygame Sound object from the file at str filepath. If 
    that file is not a .wav or is corrupt in some way raise a TypeError.'''
    
    # Check if the file exists
    if not os.access(filepath, os.F_OK):
        raise Exception("This file does not exist.")
    
    # Check if it is a .wav file
    if sndhdr.what(filepath):
        assert sndhdr.what(filepath)[0] == 'wav', "The file is not a .wav file"
    
    # Check the compression. Wave_read.getcomptype() will raise an Error if it is
    # compressed.
    wav = wave.open(filepath, 'r')
    try:
        wav.getcomptype()
    except:
        raise TypeError("This .wav file is compressed.")
    wav.close()
    
    return pygame.mixer.Sound(filepath)


def create_pygame_sound(s):
    '''Return a pygame sound object with s number of silent samples.'''

    if DEFAULT_CHANNELS == 1:
        
        # numpy.zeros returns an array object with all 0s in the
        # specified encoding. In sound terms, this is silence.
        sample_array = numpy.zeros(s, AUDIO_ENCODINGS[DEFAULT_ENCODING])
    else:
        sample_array = numpy.zeros((s, 2), AUDIO_ENCODINGS[DEFAULT_ENCODING])
    return sample_array_to_pygame(sample_array)


def create_sine_wave(hz, amp, samp):
    '''Return a pygame sound samp samples long in the form of a sine wave 
    with frequency hz and amplitude amp in the range [0, 32767].'''
    
    # Default frequency is in samples per second
    samples_per_second = float(DEFAULT_SAMP_RATE)
    
    # Hz are periods per second
    seconds_per_period = 1.0 / hz
    samples_per_period = samples_per_second * seconds_per_period
    if DEFAULT_CHANNELS == 1:
        samples = numpy.array(range(samp), 
                              numpy.float)
    else:
        samples = numpy.array([range(samp), range(samp)], 
                              numpy.float)
        samples = samples.transpose()
    
    # For each value in the array multiply it by 2 pi, divide by the 
    # samples per period, take the sin, and multiply the resulting
    # value by the amplitude.
    samples = numpy.sin((samples * 2.0 * math.pi) / samples_per_period) * amp
    
    # Convert the array back into one with the appropriate encoding
    
    samples = numpy.array(samples, AUDIO_ENCODINGS[DEFAULT_ENCODING])
    
    return sample_array_to_pygame(samples)


def pygame_to_sample_array(pygame_snd):
    '''Return a numpy array object, which allows direct access to specific
    sample values in the buffer of the pygame.mixer.Sound object pygame_snd.'''
     
    data = pygame_snd.get_buffer()
    
    # Create a numpy array from the buffer with the default encoding
    array = numpy.frombuffer(data, AUDIO_ENCODINGS[DEFAULT_ENCODING])
    
    # If there are two channels make the array object 2D
    if DEFAULT_CHANNELS == 2:
        array.shape = (len(array) / 2, 2)
    return array


def sample_array_to_pygame(samp_array):
    '''Return a new pygame.mixer.Sound object from a numpy array object 
    samp_array. Requires that samp_array is an appropriate 1D or 2D shape.'''

    shape = samp_array.shape
    
    # Check if array has the right shape
    if DEFAULT_CHANNELS == 1:
        if len (shape) != 1:
            raise ValueError("Array must be 1-dimensional for mono sound")
    else:
        if len (shape) != 2:
            raise ValueError("Array must be 2-dimensional for stereo sound")
        elif shape[1] != DEFAULT_CHANNELS:
            raise ValueError("Array depth must match number of sound channels")
    
    return pygame.mixer.Sound(samp_array)


def _draw_dot(pix, x, y, color_tuple):
    '''Draw a 3 X 3 pixel dot on PixelAccess object pix with center (x, y).'''
    
    pix[x, y] = color_tuple
    pix[x + 1, y] = color_tuple
    pix[x - 1, y] = color_tuple
    pix[x, y + 1] = color_tuple
    pix[x, y - 1] = color_tuple
    pix[x + 1, y - 1] = color_tuple
    pix[x - 1, y - 1] = color_tuple
    pix[x + 1, y + 1] = color_tuple
    pix[x - 1, y + 1] = color_tuple
