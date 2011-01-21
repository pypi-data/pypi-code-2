#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'Impromptu',
    version = '0.1.1b',
    description = 'A graphical teleprompter-like scrolling HTML text display',
    keywords = 'html, pyglet, gui, scrolling',
    author = 'Christopher Arndt',
    author_email = 'chris@chrisarndt.de',
    url = 'http://chrisarndt.de/projects/impromptu/',
    download_url = 'http://chrisarndt.de/projects/impromptu/download/',
    license = 'MIT License',
    long_description = """\
This is a little Python script, which displays a pseudo-HTML file in a window
and scrolls the text in upwards or downwards direction.

You can use it, for example, as a teleprompter while recording a podcast or
an audiobook or for a presentation. You can use differents fonts, colors and
sizes via a subset of the HTML4 standard and control the scrolling speed
and direction via command line options and keyboard commands while the
application is running.

It requires pyglet_.

.. _pyglet: http://www.pyglet.org/
""",
    platforms = 'POSIX, Windows, MacOS X',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Multimedia :: Graphics :: Presentation'
    ],
    scripts = ['impromptu.py'],
    install_requires = [
        'pyglet'
    ],
)
