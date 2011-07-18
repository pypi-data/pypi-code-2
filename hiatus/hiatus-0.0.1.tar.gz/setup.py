from distutils.core import setup

setup(
    name = "hiatus",
    version = "0.0.1",
    packages = ["hiatus"],
    description = "set_timeout/clear_timeout and set_interval/clear_interval"
                + "implemented with the threading module.",
    author = "Joshua Holbrook",
    author_email = "josh.holbrook@gmail.com",
    url = "https://github.com/jesusabdullah/hiatus",
    keywords = ["timeout", "interval", "setTimeout", "setInterval"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7", #only one tested
        "Topic :: Other/Nonlisted Topic"
    ],
    long_description = """\
hiatus
======

Hiatus is a python library that uses the ``threading`` module's "Timer" to
implement analogues to javascript's ``setTimeout``/``clearTimeout`` and
``setInterval``/``clearInterval``.

These functions may be used as decorators. Also important is
that the python analogues take time arguments in *seconds*, not
*milliseconds*, in order to be consistent with the standard library.

A Caveat:
=========

Much of python does not "play nice" with threading. You have been warned.

(I looked into a signal-based approach, but this is limited. Another approach would be to depend on an event loop, such as ``twisted.reactor``.)

Examples:
=========

::

    >>> from hiatus import set_interval
    >>> @set_interval(1.00)
    ... def dave_grohl():
    ...     print "THE BEST"
    ... 
    >>> THE BEST
    THE BEST
    THE BEST
    THE BEST
    THE BEST

::

    >>> def note():
    ...     print "HUGE SUCCESS"... 
    >>> hiatus.set_timeout(lambda: hiatus.clear_interval(glados), 6.0)
    <hiatus.set_timeout object at 0xb770468c>
    >>> glados = hiatus.set_interval(note, 1.000)
    >>> HUGE SUCCESS
    HUGE SUCCESS
    HUGE SUCCESS
    HUGE SUCCESS

For more:
=========

Visit <https://github.com/jesusabdullah/hiatus> .
    """
)
