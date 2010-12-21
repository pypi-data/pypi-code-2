# -*- coding: utf-8 -*-
# docs/example.py

"""Trivial and silly example of m4us."""


from __future__ import print_function
from cStringIO import StringIO

from zope.interface import classProvides
from m4us.api import (coroutine, is_shutdown, ProducerFinished, Component,
  ICoroutineFactory, Pipeline, PostOffice, Scheduler)


TEXT = """\
Line 1
Line 2
Line 3
"""


def main():
    """Print the repr() of each line of TEXT, followed by a line count."""
    source = lines_producer(StringIO(TEXT))
    filter_ = Counter()
    sink = repr_consumer()
    pipeline = Pipeline(source, filter_, sink)
    post_office = PostOffice()
    scheduler = Scheduler(post_office)
    post_office.link(*pipeline.links)
    scheduler.add(*pipeline.coroutines)
    scheduler.run()
    print('Line count:', filter_.count)


@coroutine(lazy=False)
def lines_producer(file_):
    """Emit lines from a file as messages."""
    inbox, message = (yield)
    for line in file_:
        if is_shutdown(inbox, message):
            yield 'signal', message
            break
        inbox, message = (yield 'outbox', line)
    (yield 'signal', ProducerFinished())


@coroutine()
def repr_consumer():
    """Print to stdout."""
    while True:
        inbox, message = (yield)
        if is_shutdown(inbox, message):
            yield 'signal', message
            break
        print(repr(message))


class Counter(Component):

    """Count messages and pass them through."""

    classProvides(ICoroutineFactory)

    def _main(self):
        """Main loop for this component."""
        self.count = 0
        inbox, message = (yield)
        while True:
            if is_shutdown(inbox, message):
                yield 'signal', message
                break
            self.count += 1
            inbox, message = (yield 'outbox', message)


if __name__ == '__main__':
    main()
