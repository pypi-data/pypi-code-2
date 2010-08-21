#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This module is free software. It is based on the short code snippet
# available at
# <http://www.cairographics.org/cairo_rsvg_and_python_in_windows/>.
# The site mentions no license, but considering that other samples on
# the website are released into the public domain, this small code
# snippet should also be considered completely free of any
# restrictions. In short: consider this file to be a) in the public
# domain or b) released under a simple all-permissive license.

try:
    import rsvg
except ImportError:
    import os
    if os.name != 'nt':
        raise ImportError('The rsvg module is not installed')
    else:
        # The operating system is, sadly, MS Windows. The code below
        # should allow rsvg to work in Python, but it has not been
        # tested.
        from ctypes import CDLL

        class rsvgHandle:
            class RsvgDimensionData(Structure):
                _fields_ = [("width", c_int),
                            ("height", c_int),
                            ("em", c_double),
                            ("ex", c_double)]

            class PycairoContext(Structure):
                _fields_ = [("PyObject_HEAD", c_byte * object.__basicsize__),
                            ("ctx", c_void_p),
                            ("base", c_void_p)]

            def __init__(self, module, path):
                self.lib = module.lib
                self.path = path
                self.handle = l.rsvg_handle_new_from_file(self.path, '')

            def get_dimension_data(self):
                svg_dim = self.RsvgDimensionData()
                self.lib.rsvg_handle_get_dimensions(self.handle,byref(svg_dim))
                return svg_dim.width, svg_dim.height

            def render_cairo(self, ctx):
                ctx.save()
                z = self.PycairoContext.from_address(id(ctx))
                self.lib.rsvg_handle_render_cairo(self.handle, z.ctx)
                ctx.restore()

        class rsvgFakeModule:
            def __init__(self):
                self.lib = CDLL('librsvg-2-2.dll')
                libgobject = CDLL('libgobject-2.0-0.dll')
                libgobject.g_type_init()

            def Handle(self, filename):
                return rsvgHandle(self, filename)

        rsvg = rsvgFakeModule()
