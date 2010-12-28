#!/usr/bin/env python
# -*- coding: utf-8 -*-

# alart: an alarming, alerting pseudo-random art generator
# Copyright (C) 2010  Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

## Maintainer: Niels Serup <ns@metanohi.org>

"""
alart generates pseudo-random art. You can adjust only what size the
image should be and what output formats should be used.

Supported output formats: pygame, svg, png, pdf, ps, eps.

Normal usage::

  import alart
  gen = alart.Alart((width, height), ('format1', 'format2'))
  data = gen.generate()

alart depends on cairo.
"""

from __future__ import with_statement # For Python 2.5
import cairo
import math
import random as default_random
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

_supported_formats = 'pygame', 'svg', 'png', 'pdf', 'ps', 'eps'

class OldVersion(Exception):
    pass

class SurfaceContext(object):
    """A virtual context with surface and file attributes"""
    def __init__(self, context, surface=None, fobj=None):
        self.context = context
        self.surface = surface
        self.file = fobj
        self.finished = False

    def flush(self):
        """Flush the surface"""
        return self.surface.flush()

    def finish(self):
        """Finish the surface"""
        if not self.finished:
            self.finished = True
            return self.surface.finish()

class MultiContext(object):
    """
    A virtual context supporting an arbitrary amount of surface
    contexts. When a context function is attempted executed in a
    MultiContext, it it sent to all the subcontexts where it will be
    executed properly.
    """
    def __init__(self, *contexts):
        self.contexts = list(contexts)

    def add(self, context):
        self.contexts.append(context)

    def _generic(self, *args):
        for ctx in self.contexts:
            ctx.context.__getattribute__(self.func)(*args)

    def flush(self):
        """Flush the surfaces of the contexts"""
        for ctx in self.contexts:
            ctx.flush()

    def finish(self):
        """Finish the surfaces of the contexts"""
        for ctx in self.contexts:
            ctx.finish()

    def __getattr__(self, attr):
        self.func = attr
        return self._generic

class Alart(object):
    """An art generator"""
    def __init__(self, size=(640, 480), formats=('pygame', 'svg'),
                 random_holder=None):
        """
        ``size`` should be a tuple of (width, height), and ``formats``
        should be a tuple of formats. To use a random number generator
        other than Python's default one, set ``random_holder`` to an
        object with a ``random()`` function and a ``randint()``
        function.
        """
        self.size = size
        for x in formats:
            if x not in _supported_formats:
                raise ValueError('unsupported format: %s' % repr(x))
        self.formats = formats

        global random
        if random_holder is not None:
            random = random_holder
        else:
            random = default_random

    def generate(self):
        """
        Generate the art. This can be run more than once and returns a
        dict with the requested data. If you initiated Alart with the
        formats ('svg', 'pdf'), for example, this function will return
        a dict {'svg': '...svg data...', 'pdf': '...pdf data...'}.
        """
        self.context = MultiContext()
        if 'pygame' in self.formats:
            self.display = True
            global pygame; import pygame
            pygame.display.init()
            self.pg_screen = pygame.display.set_mode(self.size, 0, 32)
            pygame.display.set_caption('alart')
            self.pg_context = \
                self.get_context_from_pg_surf(self.pg_screen)
            self.context.add(self.pg_context)
        else:
            self.display = False

        # Create contexts
        if 'png' in self.formats:
            if 'pygame' in self.formats:
                self.png_context = self.pg_context
            else:
                self.png_context = self.create_image_context()
                self.context.add(self.png_context)

        if 'svg' in self.formats:
            self.svg_context = self.create_svg_context()
            self.context.add(self.svg_context)

        if 'pdf' in self.formats:
            self.pdf_context = self.create_pdf_context()
            self.context.add(self.pdf_context)

        if 'ps' in self.formats:
            self.ps_context = self.create_ps_context()
            self.context.add(self.ps_context)

        if 'eps' in self.formats:
            try:
                self.eps_context = self.create_ps_context(True)
            except AttributeError, e:
                raise OldVersion('version of cairo too old; %s' % e)
            self.context.add(self.eps_context)

        # Draw it
        self.draw()

        # Get the image data and return it
        data = {}
        if 'pygame' in self.formats:
            # But first display it
            clock = pygame.time.Clock()
            done = False

            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.draw()
                        elif event.key == pygame.K_ESCAPE:
                            done = True
                clock.tick(10)

        if 'png' in self.formats:
            fobj = StringIO.StringIO()
            self.png_context.surface.write_to_png(fobj)
            self.png_context.finish()
            data['png'] = fobj.getvalue()

        if 'svg' in self.formats:
            self.svg_context.finish()
            data['svg'] = \
                self.svg_context.file.getvalue().replace('pt"', 'px"')

        if 'pdf' in self.formats:
            self.pdf_context.finish()
            data['pdf'] = self.pdf_context.file.getvalue()

        if 'ps' in self.formats:
            self.ps_context.finish()
            data['ps'] = self.ps_context.file.getvalue()

        if 'eps' in self.formats:
            self.eps_context.finish()
            data['eps'] = self.eps_context.file.getvalue()

        return data

    def get_context_from_pg_surf(self, pygame_surf):
        width, height = pygame_surf.get_size()
        cairo_surface = cairo.ImageSurface.create_for_data(
            pygame_surf.get_buffer(), cairo.FORMAT_ARGB32,
            width, height, width * 4)
        ctx = cairo.Context(cairo_surface)
        return SurfaceContext(ctx, cairo_surface)

    def create_image_context(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     self.size[0], self.size[1])
        return SurfaceContext(cairo.Context(surface), surface)

    def create_svg_context(self):
        fobj = StringIO.StringIO()
        surface = cairo.SVGSurface(fobj, self.size[0], self.size[1])
        return SurfaceContext(cairo.Context(surface), surface, fobj)

    def create_pdf_context(self):
        fobj = StringIO.StringIO()
        surface = cairo.PDFSurface(fobj, self.size[0], self.size[1])
        return SurfaceContext(cairo.Context(surface), surface, fobj)

    def create_ps_context(self, encapsulated=False):
        fobj = StringIO.StringIO()
        surface = cairo.PSSurface(fobj, self.size[0], self.size[1])
        if encapsulated:
            surface.set_eps(True)
        return SurfaceContext(cairo.Context(surface), surface, fobj)

    def get_points(self):
        """Calculate and return the points needed for silhouette"""
        choose = random.randint(-1, 3)
        if choose <= 0:
            points_num = random.randint(100, 200)
            size_min = random.random() * 0.2 + 0.2
        elif choose == 1:
            points_num = random.randint(201, 500)
            size_min = random.random() * 0.04 + 0.04
        elif choose == 2:
            points_num = random.randint(500, 1000)
            size_min = random.random() * 0.02 + 0.02
        elif choose == 3:
            points_num = random.randint(1001, 3000)
            size_min = random.random() * 0.01 + 0.01

        size_max = random.random() * 0.2 + 0.7
        angle_change = 2 * math.pi / points_num
        threshold = random.random() * 0.2 + 0.1
        threshold_nums = math.ceil(1 / threshold)
        prev_factor = random.random()

        center = (random.randint(int(self.size[0] * 0.1),
                                 int(self.size[0] * 0.9)),
                  random.randint(int(self.size[1] * 0.1),
                                 int(self.size[1] * 0.9)))
        x_len = (center[0], self.size[0] - center[0])
        y_len = (center[1], self.size[1] - center[1])

        state = 1
        # There are five states:
        #
        #    _____3_____
        #   ,___________,
        # | |           | |
        # | |           | 2
        # 4 |           | |
        # | |___________| |
        #    __5__ __1__
        #
        # State 1 and 5 are technically the same.
        # For each angle, the longest length from the center to the
        # side of the rectangle is calculated. A random length is then
        # chosen, after which a position is calculated and yielded.
        for i in xrange(points_num):
            angle = i * angle_change
            if state == 1:
                rect_bottom_len = math.tan(angle) * y_len[1]
                if not rect_bottom_len < x_len[1]:
                    state = 2
                else:
                    max_len = y_len[1] / math.cos(angle)
            if state == 2:
                rect_right_len = math.tan(angle - math.pi / 2) * x_len[1]
                if not rect_right_len < y_len[0]:
                    state = 3
                else:
                    max_len = x_len[1] / math.cos(angle - math.pi / 2)
            if state == 3:
                rect_top_len = math.tan(angle - math.pi) * y_len[0]
                if not rect_top_len < x_len[0]:
                    state = 4
                else:
                    max_len = y_len[0] / math.cos(angle - math.pi)
            if state == 4:
                rect_left_len = math.tan(angle - math.pi * 1.5) * x_len[0]
                if not rect_left_len < y_len[1]:
                    state = 5
                else:
                    max_len = x_len[0] / math.cos(angle - math.pi * 1.5)
            if state == 5:
                max_len = y_len[1] / math.cos(angle)

            factor = prev_factor + (random.random() - 0.5) * threshold * 2

            if i == 0:
                first_factor = factor
            elif i >= points_num - threshold_nums:
                # These are the final points. The final point will be
                # connected with the first point, so these small
                # checks are needed. If the size of the current factor
                # would force future factors to be stretched with
                # differences above threshold, it is un-randomized and
                # replaced with a factor that makes the factor closer
                # to the first factor.
                f_subr = first_factor - factor
                f_diff = abs(f_subr)
                threshold_next_loop_left = (points_num - i - 1) * threshold
                if f_diff > threshold_next_loop_left:
                    factor = prev_factor + threshold * cmp(f_subr, 0)
            if factor > 1:
                factor = 1
            elif factor < 0:
                factor = 0

            size_factor = factor * (size_max - size_min) + size_min
            out_len = max_len * size_factor
            prev_factor = factor
            pos = (math.sin(angle), math.cos(angle))
            pos = [pos[i] * out_len + center[i] for i in range(2)]
            yield pos

    def curve_point(self, pos, prev_pos, next_pos):
        """
        Calculate control points meant to give the drawing a fairly
        smooth look, and write to context.
        """

        curving = random.random() * 0.1 + 0.05

        # Find the point in the the middle of the line created by
        # prev_pos and next_pos
        m_subr = [next_pos[i] - prev_pos[i] for i in range(2)]
        m_pos = [prev_pos[i] + m_subr[i] / 2 for i in range(2)]

        # Calculate the length and angle of the line created by m_pos
        # and pos
        p_subr = [pos[i] - m_pos[i] for i in range(2)]
        p_len = math.sqrt(p_subr[0] ** 2 + p_subr[1] ** 2)
        p_angle = math.atan2(p_subr[1], p_subr[0])

        # Create two control points close to pos
        ctrl1 = (math.cos(p_angle + curving), math.sin(p_angle + curving))
        ctrl1 = [ctrl1[i] * p_len + prev_pos[i] for i in range(2)]
        ctrl2 = (math.cos(p_angle - curving), math.sin(p_angle - curving))
        ctrl2 = [ctrl2[i] * p_len + prev_pos[i] for i in range(2)]

        # Draw to context
        self.context.curve_to(ctrl1[0], ctrl1[1], ctrl2[0], ctrl2[1], pos[0], pos[1])

        # Uncomment to see control points
        # ctx = self.context
        # ctx.move_to(*prev_pos)
        # ctx.line_to(pos[0], pos[1])
        # ctx.rectangle(pos[0] - 2, pos[1] - 2, 4, 4)
        # ctx.rectangle(ctrl1[0] - 1, ctrl1[1] - 1, 2, 2)
        # ctx.rectangle(ctrl2[0] - 1, ctrl2[1] - 1, 2, 2)

    def draw(self):
        """Draw the silhouettes"""
        self.context.set_source_rgba(random.random(), random.random(),
        random.random(), 1.0)
        self.context.paint()

        for x in range(random.randint(2, 10)):
            self.draw_shape()

        if 'pygame' in self.formats:
            pygame.display.flip()

    def draw_shape(self):
        """Draw one silhouette"""
        ctx = self.context
        ctx.set_source_rgba(random.random(), random.random(),
                            random.random(), random.random())

        points = self.get_points()
        start_pos = points.next()
        prev_pos = start_pos
        pos = points.next()
        ctx.move_to(*prev_pos)
        for next_pos in points:
            self.curve_point(pos, prev_pos, next_pos)
            prev_pos = pos
            pos = next_pos
        self.curve_point(pos, prev_pos, start_pos)
        ctx.close_path()
        ctx.fill()

    def end(self):
        try:
            self.context.finish()
        except AttributeError:
            pass

    def __del__(self):
        self.end()

    def __exit__(self):
        """Finish the surfaces that have not already been finished"""
        self.end()



def command_line_entry(args=None, random_holder=None):
    """
    Allow easy use from the command-line. If ``args`` is None,
    ``sys.argv[1:]`` is be used. ``random_holder`` can be set to use
    other random functions than Python's internal. A special random
    function cannot be set using the command-line.
    """
    import sys
    from optparse import OptionParser
    class ModifiedOptionParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    parser = ModifiedOptionParser(
        prog='alart',
        usage='Usage: %prog [OPTION]... [OUTPUT]...',
        description='Generate pseudo-random art',
        version='''\
alart 0.1.0 "Ablaze"
Copyright (C) 2010  Niels Serup
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''',
        epilog='''
If the generated image is to be displayed in a PyGame window (the
default option), a new one can be generated in its place by pressing
R. Closing the window is done by pressing ESCAPE. If alart is to
output the image to a file after having shown it, it will always save
the last image to be generated. Previous images will be lost.

alart supports these output formats: svg, png, pdf, ps (PostScript),
eps (Encapsulated PostScript). It will attempt to guess output formats
from filename extensions, but when this is not possible, use the
-t|--type option. The '-' can be used for printing to standard out.

Examples:
  alart
    display generated image with PyGame

  alart -D out.svg
    output generated image as SVG to `out.svg'

  alart -D -t png png-out -t svg svg-out
    output image as PNG to `png-out' and as SVG to `svg-out'. In this
    case, the type must be given because there is no filename extension
    such as `.png' or `.svg'.

  alart -s 400x400 cool-art.pdf -t ps -
    display 400x400 image in a PyGame window until you close the
    window, after which the image will be saved as PDF to
    `cool-art.pdf' and as SVG to standard out.
''')

    parser.add_option('-s', '--size', dest='size',
                      metavar='WIDTHxHEIGHT', help='''\
set the size of the image (defaults to 640x480)
''')

    parser.add_option('-D', '--no-display', dest='display',
                      action='store_false', default=True, help='''\
do not display the generated image
''')

    parser.add_option('-t', '--type', dest='type_given',
                      metavar='TYPE', action='append',
                      default=[], nargs=2, help='''\
set the type of a OUTPUT (should be set just before the OUTPUT)
''')

    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)

    size = options.size
    if not size:
        size = (640, 480)
    else:
        try:
            size = tuple(int(x) for x in size.split('x'))
        except Exception:
            parser.error('incorrect syntax: %s' % size)
    
    output = list(options.type_given)
    for x in args:
        try:
            output.append((x.rsplit('.')[1], x))
        except IndexError:
            parser.error('format of output file %s cannot be determined'
                         % repr(x))
    if [x[1] for x in output].count('-') > 1:
        parser.error('only the contents of one file can be sent to standard out')

    output_dict = {}
    for x in output:
        if not x[0] in output_dict:
            output_dict[x[0]] = []
        output_dict[x[0]].append(x[1])
    
    formats = [x[0] for x in output]
    if options.display:
        formats.append('pygame')
    formats = tuple(set(formats))

    try:
        alart = Alart(size, formats, random_holder)
    except ValueError, e:
        parser.error(e)

    try:
        try:
            data = alart.generate()
        except OldVersion, e:
            parser.error(e)
        for format, bytes in data.iteritems():
            for x in output_dict[format]:
                if x != '-':
                    with open(x, 'wb') as f:
                        f.write(bytes)
                else:
                    sys.stdout.write(bytes)
    except (EOFError, KeyboardInterrupt):
        pass
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        alart.end()

if __name__ == '__main__':
    command_line_entry()
