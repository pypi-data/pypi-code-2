#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import subprocess
import os
import sys
import re
import math

def escape_shell_arg(arg):
    """
    Escape a string to be used as a shell argument

    Adds single quotes around a string and quotes/escapes
    any existing single quotes allowing you to pass a string directly to a
    shell function and having it be treated as a single safe argument.
    
    This function should be used to escape individual arguments to shell
    functions coming from user input. 

    `arg` - The argument that will be escaped.
    """
    return '\'' + arg.replace('\'', '\'' + '\\' + '\'' + '\'') + '\''

class UtilityNotFound(Exception):
    """
    Exception that raises when required utility is not found in $PATH
    """

class CodecNotFound(Exception):
    """
    Exception that raises when trying convert video within unknown codec
    """

class WrongCommandLine(Exception):
    """
    Exception that raises when trying convert video within unknown codec
    """

class ConvertResult(object):
    """
    Result object
    """
    STATE_SUCCESS = True
    STATE_FAILURE = False

    # Absolute path to source file
    movie_original = ''

    # Absolute path to result file
    movie_converted = ''

    # Success converted flag (mencoder)
    converted = False

    # Movie metadata dictionary
    metadata = {}

    # Converted movie snapshots
    snapshots = {}

class Converter(object):
    """
    The mencoder API wrapper class
    """
    # Default output movie frame width
    width  = None

    # Default output movie frame height
    height = None

    # Default output movie sample rate
    sample_rate = 22050

    # Default output movie containter
    output_format = 'lavf'

    # Default output movie video codec
    video_codec = 'lavc'

    # Default video codec options
    video_opts = None

    # Default video codec options prefix
    video_opts_prefix = ''   

    # Default output movie audio codec
    audio_codec = 'lavc'

    # Default audio codec options
    audio_opts = None

    # Default audio codec options prefix
    audio_opts_prefix = ''

    # Path to `mencoder` binary
    MENCODER_CMD = 'mencoder'

    # Path to `mplayer` binary
    MPLAYER_CMD = 'mplayer'

    # Path to `yamdi` binary
    YAMDI_CMD = 'yamdi'

    # Path to `ffmpeg` binary
    FFMPEG_CMD = 'ffmpeg'

    # Path to `ffmpeg2theora`
    FFMPEGTOTHEORA_CMD = 'ffmpeg2theora'

    def __init__(self, *args, **kwargs):
        """
        The class constructor
        """
        self.MENCODER_CMD = kwargs.get('mencoder') or self.MENCODER_CMD 
        self.MPLAYER_CMD  = kwargs.get('mplayer')  or self.MPLAYER_CMD
        self.YAMDI_CMD    = kwargs.get('yamdi')    or self.YAMDI_CMD
        self.FFMPEG_CMD   = kwargs.get('ffmpeg')   or self.FFMPEG_CMD
        self.FFMPEGTOTHEORA_CMD = kwargs.get('ffmpeg2theora') or self.FFMPEGTOTHEORA_CMD

        self.width  = kwargs.get('width') or self.width
        self.height = kwargs.get('height') or self.height 

        self.test_env()

    def __repr__(self):
        """
        Text represent
        """
        return 'Converter into {video} codec'.format(video=self.video_codec)

    def test_env(self):
        """
        Check the environment:
         
         - tries to call required utilites and raise exception if test fails;
         - checks that given codec is available or raises
          
        """
        commands = [
            self.MENCODER_CMD, 
            self.MPLAYER_CMD, 
            self.YAMDI_CMD,
            self.FFMPEG_CMD,
            self.FFMPEGTOTHEORA_CMD,
        ]

        for cmd in commands:
            try:
                subprocess.check_call([cmd, '--help'], 
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE,
                )

            except OSError, e:
                raise UtilityNotFound, 'Utility %s not found' % cmd

            except subprocess.CalledProcessError, e:
                pass

        # @TODO Check codec

    def get_encode_command(self, input_file, output_file):
        """
        Return `mencoder` console command to convert movie
        """
        def input_filename():
            """
            Returns a input filename argument substring
            """
            return escape_shell_arg(input_file)

        def output_filename():
            """
            Returns a output filename (-o) argument substring
            """
            return '-o {output_file}'.format(output_file=output_file)

        def container():
            """
            Returns a output format (-of) argument substring
            """
            return '-of {format}'.format(format=self.output_format)

        def vcodec():
            """
            Returns a video codec (-ovc) argument substring
            """
            return '-ovc {video_codec}'.format(video_codec=self.video_codec)

        def vcodec_opts():
            """
            Returns a video codec options argument substring
            """
            if not self.video_opts:
                return ''

            param = '{codec}opts'.format(codec=self.video_codec)

            if self.video_opts_prefix:
                param = self.video_opts_prefix

            return '-{param} {opts}'.format(
                param = param,
                opts  = self.video_opts
            )           

        def acodec():
            """
            Returns a audio codec (-oac) argument substring
            """
            if not self.audio_codec:
                return ''
            return '-oac {audio_codec}'.format(audio_codec=self.audio_codec)

        def acodec_opts():
            """
            Returns a audio codec options argument substring
            """
            if not self.audio_opts:
                return ''
            param = '{audio_codec}opts'.format(audio_codec=self.audio_codec)

            if self.audio_opts_prefix:
                param = self.audio_opts_prefix
            return '-{param} {opts}'.format(
                param = param,
                opts  = self.audio_opts
            )
        
        def sample_rate():
            """
            Returns a sample rate (-srate) argument substring
            """
            return '-srate %s' % self.sample_rate if self.sample_rate else ''

        def video_filters():
            """
            Returns a video filters (-vf) argument substring
            """
            bits = []

            if self.width and self.height:
                bits.append('scale={w}:{h}'.format(w=self.width,h=self.height))

            elif self.width and not self.height:
                bits.append('scale={w}:-'.format(w=self.width))

            elif not self.width and self.height:
                bits.append('scale=-:{h}'.format(h=self.height))

            return ('-vf '+','.join(bits)) if bits else ''

        cmd = ' '.join([self.MENCODER_CMD,
            input_filename(),    # Input filename
            output_filename(),   # Output filename (-o argument)
            container(),         # Format container (-of argument)
            vcodec(),            # Video codec (-ovc argument)
            vcodec_opts(),       # Video codec options
            acodec(),            # Audio codec (-oac argument)
            acodec_opts(),       # Audio codec options string
            sample_rate(),       # Sample rate
            video_filters(),     # Video filters (-vf argument) substring
        ])
        print cmd
        return cmd

    def get_movie_info(self, input_file):
        """
        Retrieve all metadata such as frame width, height, rate, audio and
        video codecs, duration and so on.
        """
        info_map, meta_data = (
            ('ID_AUDIO_CODEC',       'audio_codec',       [unicode]),
            ('ID_AUDIO_FORMAT',      'audio_format',      [unicode]),
            ('ID_AUDIO_BITRATE',     'audio_bitrate',     [int]),
            ('ID_AUDIO_RATE',        'audio_rate',        [int]),
            ('ID_AUDIO_NCH',         'audio_nch',         [int]),
            ('ID_VIDEO_FORMAT',      'video_format',      [unicode]),
            ('ID_VIDEO_BITRATE',     'video_bitrate',     [int]),
            ('ID_VIDEO_ASPECT',      'video_aspect',      [float]),
            ('ID_VIDEO_WIDTH',       'width',             [int]),
            ('ID_VIDEO_HEIGHT',      'height',            [int]),         
            ('ID_VIDEO_FPS',         'frame_rate',        [float]),
            ('ID_LENGTH',            'duration',          [float, math.ceil, int]),
            ('ID_CLIP_INFO_VALUE0',  'clip_info_value0',  [unicode]),
            ('ID_VIDEO_ID',          'video_id',          [int]),
            ('ID_AUDIO_ID',          'audio_id',          [int]),
            ('ID_CLIP_INFO_N',       'clip_info_n',       [unicode]),
            ('ID_FILENAME',          'filename',          [unicode]),
            ('ID_DEMUXER',           'demuxer',           [unicode]),
            ('ID_SEEKABLE',          'seekable',          [bool]),
            ('ID_CHAPTERS',          'chapters',          [int]),
            ('ID_VIDEO_CODEC',       'video_codec',       [unicode]),
            ('ID_EXIT',              'exit',              [unicode]),
        ), {}

        # mplayer -vo null -ao null -frames 0 -identify %s' % file
        stream = subprocess.Popen(
            ' '.join([self.MPLAYER_CMD,
            '-vo null',
            '-ao null',
            '-frames 0',
            '-identify',
            '"{file}"'.format(file=input_file),
            ]),
            shell  = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True
        ).stdout   

        while True:
            line = stream.readline()

            if not line:
                break

            if not line.startswith('ID_'):
                continue

            # Meta info
            for token, field, filters  in info_map:
                if line.startswith(token):
                    key, val = line.strip().split('=', 2)

                    for f in filters:
                        val = f(val)
                    meta_data[field] = val
                # if
            # for
        # while
        return meta_data

    def snapshot_filename(self, result, second):
        """
        Returns snapshot filename
        """
        return '{video_file}_{second}.jpeg'.format(
            video_file = result.movie_converted,
            second     = second,
        )

    def make_snapshot(self, result, num=10): 
        """
        Make snapshots
        """
        # ffmpeg -i out.flv -an -ss 5 -r 1 -vframes 1 -s 320x240 -y -f mjpeg test.jpg
        duration = result.movie_info['duration'] 
        width    = result.movie_info['width']
        height   = result.movie_info['height']

        seconds = list(xrange(1, duration, int(math.floor(float(duration / num)))))
        seconds.append(duration)
        seconds.append( math.ceil(float(duration) /2) )

        for s in seconds:
            s = int(s)

            snapshot_file = '{video_file}_{second}.jpeg'.format(
                video_file = result.movie_converted,
                second = s,
            )

            thumb_filename = self.snapshot_filename(result, s)

            if thumb_filename is None:
                continue

            stream = subprocess.Popen(' '.join(
                [
                    self.FFMPEG_CMD,
                    '-i {file}'.format(file=escape_shell_arg(result.movie_converted)),
                    '-an',
                    '-ss {second}'.format(second=s),
                    '-vframes 1',
                    '-y',
                    '-f mjpeg',
                    '-s {width}x{height}'.format(width=width,height=height),
                    escape_shell_arg(thumb_filename),
                ]),
                shell = True,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                universal_newlines = True             
            )

            while True:
                line = stream.stdout.read()
                if not line:
                    break
                print line

            # Avoid empty snapshots
            if os.path.getsize(snapshot_file) > 0:
                result.snapshots[s] = snapshot_file
            else:
                os.remove(snapshot_file)

    # mplayer out.flv -ss 00:00:17 -frames 1 -ao null -vo png 
    def convert(self, input_file, output_file, **kwargs):
        """
        Convertion entry point 
        """
        result = ConvertResult()

        # 
        result.movie_original = input_file
        result.movie_info = self.get_movie_info(input_file)
        result.converted = self.encode(input_file, output_file, **kwargs)

        if result.converted:
            result.movie_converted = output_file            

            self.make_snapshot(result)
            self.inject_metadata(output_file)

        return result

    def inject_metadata(self, output_file):
        """
        Inject metadata into converted movie
        """
        stream  = subprocess.Popen(
            ' '.join([self.YAMDI_CMD,
            '-i %s' % escape_shell_arg(output_file),
            '-o %s' % escape_shell_arg(output_file + '.yamdi'),
            ]),
            shell  = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True
        )
        while True:
            line = stream.stdout.readline()
            if not line:
                 break
            print line
        
        os.remove(output_file)
        os.rename('%s.yamdi' % output_file, output_file)
            
    def encode(self, input_file, output_file, **kwargs):
        """
        Movie encoding with state tracking
        """
        re_progress = re.compile('^Pos:.*?\(\s*?(\d+)%\)', re.U)
        command = self.get_encode_command(input_file, output_file)

        stdout, percent, eof_count = subprocess.Popen(command,
            shell  = True, 
            stdout = subprocess.PIPE, 
            stderr = subprocess.STDOUT,
            universal_newlines = True
        ).stdout, 0, 0

        while True:
            line = stdout.readline()[:-1]

            # Break infinite loop if EOF exceed
            if len(line) < 1:
                if eof_count > 5:
                    break
                else:
                    eof_count += 1
                    continue
            else:
                eof_count = 0

            if 'Error parsing option on the command line' in line:
                raise WrongCommandLine, 'Parse error in command:\n%s\n' % command

            # Retrieve current progress position
            pos_match = re_progress.match(line)

            if pos_match:
                curr = pos_match.group(1)

                if percent != curr:
                    self.process_handler(int(percent), int(curr))
                    percent = curr

        # End of loop
        return True

    def process_handler(self, old_percent, new_percent):
        """
        Convertion hook. Call on every percent change
        """
        print "Change state: %s -> %s" % (old_percent, new_percent)

class H263Converter(Converter):
    """
    The LAVC codec
    """
    video_codec = 'lavc'
    video_opts  = 'vcodec=flv:vbitrate=700:trell:v4mv:mv0:mbd=2:cbp:aic:cmp=3:subcmp=3'
    audio_codec = 'mp3lame'
    audio_opts  = 'abr:br=64'
    audio_opts_prefix = 'lameopts'

class H264Converter(Converter):
    """
    The X264 (Open h264 implementation) codec
    """    
    # mencoder 1.mpg -o 2.flv -of lavf -ovc x264 -oac mp3lame -srate 44100
    video_codec = 'x264'
    video_opts = 'vcodec=x264:vbitrate=288:mbd=2:mv0:trell:v4mv:cbp:last_pred=3:predia=2:dia=2:vmax_b_frames=0:vb_strategy=1:precmp=2:cmp=2:subcmp=2:preme=2:qns=2'
    video_opts = ''
    video_opts_prefix = 'x264encopts'
    audio_codec = 'mp3lame'
    audio_opts  = 'abr:br=64'
    audio_opts_prefix = 'lameopts'


##############################################################################

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage:\n%s <input_file> <output_file>" % sys.argv[0]
        sys.exit(1)

    converter = H264Converter(
        width  = 640,
        height = 480,
    )
    result = converter.convert(
        input_file = sys.argv[1], 
        output_file = sys.argv[2],
    )
