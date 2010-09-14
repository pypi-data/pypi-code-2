"""\

:mod:`cli.profiler` -- statistical and deterministic application profiling
--------------------------------------------------------------------------

The :class:`Profiler` can help you quickly measure your application's
overall performance or focus on specific sections.
"""

__license_ = """
Copyright (c) 2009-2010 Will Maier <will@m.aier.us>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""

try:
    from functools import update_wrapper
except ImportError: # pragma: no cover
    from cli.util import update_wrapper

from cli.util import Stats, fmtsec

__all__ = ["Profiler"]

class Profiler(object):
    """A profiling tool.

    The :class:`Profiler` provides two decorator methods which can help
    you improve the performance of your code. Arguments are:

    *stdout* is a file-like object into which the profiling report will
    be written.

    If *anonymous* is True, the profiling decorators will run in-place.
    Be careful when combining this option with *count* greater than 1 if
    the block of code in question may have side effects. This is useful
    for testing a specific block of code within a larger program; for
    example::

        profiler = Profiler(anonymous=True)

        biglist = []

        # The profiler will measure the code defined in the anonymous
        # block function and then proceed with the rest of the script.
        # Note that you must take extra precautions to make sure that
        # names defined in the anonymous block are valid outside of its
        # scope.
        @profiler.deterministic
        def block():
            global biglist
            biglist = range(10**5)

        length = len(biglist)

    *count* and *repeat* control the number of iterations the code in
    question will be run in the :meth:`statistical` profiler.
    """

    def __init__(self, stdout=None, anonymous=False, count=1000, repeat=3):
        self.stdout = stdout is None and sys.stdout or stdout
        self.anonymous = anonymous
        self.count = count
        self.repeat = repeat
        self.stats = None
        self.result = None

    def wrap(self, wrapper, wrapped):
        """Wrap callable *wrapped* with *wrapper*.

        :meth:`wrap` calls :func:`functools.update_wrapper` (or an
        equivalent implementation if not available) to preserve the
        callable's metadata. If :attr:`anonymous` is True or the
        *wrapped* callable's name is anonymous (see :meth:`isanon`),
        the wrapped callable will be executed in-place. Otherwise, the
        wrapped callable will simply be returned (like a decorator).
        """
        update_wrapper(wrapper, wrapped)

        if self.anonymous or self.isanon(wrapped.__name__):
            return wrapper()
        else:
            return wrapper

    def isanon(self, name):
        """Return True if the *name* seems to be anonymous.

        Callables whose names are "anonymous" or that start with
        "__profiler_" are considered anonymous.
        """
        return name.startswith("__profiler_") or \
            name == "anonymous"

    def deterministic(self, func):
        """Deterministically evaluate *func*'s performance.

        *func* should be a callable. It will be decorated with
        a simple function that uses the standard library's
        :class:`profile.Profile` to trace and time each step of *func*'s
        execution. After *func* is profiled, a report will be written
        to :attr:`stdout`. The profiling statistics are saved to the
        :attr:`stats` attribute after the run.
        """

        try:
            from cProfile import Profile
        except ImportError: # pragma: no cover
            from profile import Profile
        profiler = Profile()

        def wrapper(*args, **kwargs):
            self.stdout.write(u"===> Profiling %s:\n" % func.__name__)
            profiler.runcall(func, *args, **kwargs)
            self.stats = Stats(profiler, stream=self.stdout)
            self.stats.strip_dirs().sort_stats(-1).print_stats()

        return self.wrap(wrapper, func)

    def statistical(self, func):
        """Run *func* many times, reporting the best run time.

        This profiling method wraps *func* with a decorator that
        performs :attr:`repeat` runs, executing *func* :attr:`count`
        times each run. The profiler will average the execution time for
        each loop and report the best time on :attr:`stdout`. The result
        is saved at :attr:`result` -- divide this number by
        :attr:`count` to determine the average execution time.

        This profiler is useful for comparing the speed of equivalent
        implementations of similar algorithms.
        """
        try:
            from timeit import default_timer as timer
        except ImportError: # pragma: no cover
            from time import time as timer

        def timeit(func, *args, **kwargs):
            cumulative = 0
            for i in range(self.count):
                start = timer()
                func(*args, **kwargs)
                stop = timer()
                cumulative += stop - start

            return cumulative

        def repeat(func, *args, **kwargs):
            return [timeit(func, *args, **kwargs) for i in range(self.repeat)]

        def wrapper(*args, **kwargs):
            self.stdout.write(u"===> Profiling %s: " % func.__name__)
            self.result = min(repeat(func, *args, **kwargs))
            self.stdout.write(u"%d loops, best of %d: %s per loop\n" % (
                self.count, self.repeat, fmtsec(self.result/self.count)))

        return self.wrap(wrapper, func)

    __call__ = deterministic
