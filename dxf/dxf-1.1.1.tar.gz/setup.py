from setuptools import setup

setup(
    name = "dxf",
    version = "1.1.1",
    packages = [''],

    author = "Stani <stanibe@gmail.com>, Kellbot <kellbot@kellbot.com>",
    description = "Python library to generate DXF drawing files (CAD)",
    long_descriptions = """
SDXF is a Python library to generate DXF files. DXF is an abbreviation of Data Exchange File, a vector graphics file format. It is supported by virtually all CAD products (such as AutoCAD, Blender, 3Dstudio, Maya,Vectorworks...) and vector drawing programs (such as Illustrator, Flash, ...).

SDXF can generate complex CAD drawings (dxf format) with all kind of entities (such as 3DFace, Arc, Insert, Circle, Line, Mtext, Point, Polyline, Rectangle (can be filled), Solid & Text). They can be structured with Layers, Blocks, Linetypes, Text styles and Views.

Example

import sdxf
d=sdxf.Drawing()
d.append(sdxf.Text('Hello World!',point=(3,0,1)))
d.append(sdxf.Line(points=[(0,0,0),(1,1,1)]))
d.saveas('hello_world.dxf')

For more info:
http://dxf.stani.be
http://jonschull.blogspot.com/2008/12/kellbot-sdxf-python-library-for-dxf.html

Note: This exists because of defun. http://pypi.python.org/pypi/SDXF
""",
    url = "http://www.kellbot.com/sdxf-python-library-for-dxf/",
)
