import time

from collections import deque
from Queue import Queue, Empty as QueueEmpty

from celery.utils import all
from celery.utils import timeutils
from celery.utils.compat import izip_longest, chain_from_iterable


class RateLimitExceeded(Exception):
    """The token buckets rate limit has been exceeded."""


class TaskBucket(object):
    """This is a collection of token buckets, each task type having
    its own token bucket. If the task type doesn't have a rate limit,
    it will have a plain :class:`Queue` object instead of a
    :class:`TokenBucketQueue`.

    The :meth:`put` operation forwards the task to its appropriate bucket,
    while the :meth:`get` operation iterates over the buckets and retrieves
    the first available item.

    Say we have three types of tasks in the registry: ``celery.ping``,
    ``feed.refresh`` and ``video.compress``, the TaskBucket will consist
    of the following items::

        {"celery.ping": TokenBucketQueue(fill_rate=300),
         "feed.refresh": Queue(),
         "video.compress": TokenBucketQueue(fill_rate=2)}

    The get operation will iterate over these until one of the buckets
    is able to return an item. The underlying datastructure is a ``dict``,
    so the order is ignored here.

    :param task_registry: The task registry used to get the task
        type class for a given task name.


    """

    def __init__(self, task_registry):
        self.task_registry = task_registry
        self.buckets = {}
        self.init_with_registry()
        self.immediate = deque()

    def put(self, request):
        """Put a :class:`~celery.worker.job.TaskRequest` into
        the appropiate bucket."""
        if request.task_name not in self.buckets:
            self.add_bucket_for_type(request.task_name)
        self.buckets[request.task_name].put_nowait(request)
    put_nowait = put

    def _get_immediate(self):
        try:
            return self.immediate.popleft()
        except IndexError: # Empty
            raise QueueEmpty()

    def _get(self):
        # If the first bucket is always returning items, we would never
        # get to fetch items from the other buckets. So we always iterate over
        # all the buckets and put any ready items into a queue called
        # "immediate". This queue is always checked for cached items first.
        try:
            return 0, self._get_immediate()
        except QueueEmpty:
                pass

        remaining_times = []
        for bucket in self.buckets.values():
            remaining = bucket.expected_time()
            if not remaining:
                try:
                    # Just put any ready items into the immediate queue.
                    self.immediate.append(bucket.get_nowait())
                except QueueEmpty:
                    pass
                except RateLimitExceeded:
                    remaining_times.append(bucket.expected_time())
            else:
                remaining_times.append(remaining)

        # Try the immediate queue again.
        try:
            return 0, self._get_immediate()
        except QueueEmpty:
            if not remaining_times:
                # No items in any of the buckets.
                raise

            # There's items, but have to wait before we can retrieve them,
            # return the shortest remaining time.
            return min(remaining_times), None

    def get(self, block=True, timeout=None):
        """Retrive the task from the first available bucket.

        Available as in, there is an item in the queue and you can
        consume tokens from it.

        """
        time_start = time.time()
        did_timeout = lambda: timeout and time.time() - time_start > timeout

        while True:
            remaining_time, item = self._get()
            if remaining_time:
                if not block or did_timeout():
                    raise QueueEmpty
                time.sleep(min(remaining_time, timeout or 1))
            else:
                return item

    def get_nowait(self):
        return self.get(block=False)

    def init_with_registry(self):
        """Initialize with buckets for all the task types in the registry."""
        map(self.add_bucket_for_type, self.task_registry.keys())

    def refresh(self):
        """Refresh rate limits for all task types in the registry."""
        map(self.update_bucket_for_type, self.task_registry.keys())

    def get_bucket_for_type(self, task_name):
        """Get the bucket for a particular task type."""
        if task_name not in self.buckets:
            return self.add_bucket_for_type(task_name)
        return self.buckets[task_name]

    def _get_queue_for_type(self, task_name):
        bucket = self.buckets[task_name]
        if isinstance(bucket, TokenBucketQueue):
            return bucket.queue
        return bucket

    def update_bucket_for_type(self, task_name):
        task_type = self.task_registry[task_name]
        rate_limit = getattr(task_type, "rate_limit", None)
        rate_limit = timeutils.rate(rate_limit)
        task_queue = FastQueue()
        if task_name in self.buckets:
            task_queue = self._get_queue_for_type(task_name)
        else:
            task_queue = FastQueue()

        if rate_limit:
            task_queue = TokenBucketQueue(rate_limit, queue=task_queue)

        self.buckets[task_name] = task_queue
        return task_queue

    def add_bucket_for_type(self, task_name):
        """Add a bucket for a task type.

        Will read the tasks rate limit and create a :class:`TokenBucketQueue`
        if it has one. If the task doesn't have a rate limit a regular Queue
        will be used.

        """
        if task_name not in self.buckets:
            return self.update_bucket_for_type(task_name)

    def qsize(self):
        """Get the total size of all the queues."""
        return sum(bucket.qsize() for bucket in self.buckets.values())

    def empty(self):
        return all(bucket.empty() for bucket in self.buckets.values())

    def clear(self):
        for bucket in self.buckets.values():
            bucket.clear()

    @property
    def items(self):
        # for queues with contents [(1, 2), (3, 4), (5, 6), (7, 8)]
        # zips and flattens to [1, 3, 5, 7, 2, 4, 6, 8]
        return filter(None, chain_from_iterable(izip_longest(*[bucket.items
                                    for bucket in self.buckets.values()])))


class FastQueue(Queue):
    """:class:`Queue.Queue` supporting the interface of
    :class:`TokenBucketQueue`."""

    def clear(self):
        return self.queue.clear()

    def expected_time(self, tokens=1):
        return 0

    def can_consume(self, tokens=1):
        return True

    def wait(self, block=True):
        return self.get(block=block)

    @property
    def items(self):
        return self.queue


class TokenBucketQueue(object):
    """Queue with rate limited get operations.

    This uses the token bucket algorithm to rate limit the queue on get
    operations.
    See http://en.wikipedia.org/wiki/Token_Bucket
    Most of this code was stolen from an entry in the ASPN Python Cookbook:
    http://code.activestate.com/recipes/511490/

    :param fill_rate: see :attr:`fill_rate`.
    :keyword capacity: see :attr:`capacity`.

    .. attribute:: fill_rate

        The rate in tokens/second that the bucket will be refilled.

    .. attribute:: capacity

        Maximum number of tokens in the bucket. Default is ``1``.

    .. attribute:: timestamp

        Timestamp of the last time a token was taken out of the bucket.

    """
    RateLimitExceeded = RateLimitExceeded

    def __init__(self, fill_rate, queue=None, capacity=1):
        self.capacity = float(capacity)
        self._tokens = self.capacity
        self.queue = queue
        if not self.queue:
            self.queue = Queue()
        self.fill_rate = float(fill_rate)
        self.timestamp = time.time()

    def put(self, item, block=True):
        """Put an item into the queue.

        Also see :meth:`Queue.Queue.put`.

        """
        self.queue.put(item, block=block)

    def put_nowait(self, item):
        """Put an item into the queue without blocking.

        :raises Queue.Full: If a free slot is not immediately available.

        Also see :meth:`Queue.Queue.put_nowait`

        """
        return self.put(item, block=False)

    def get(self, block=True):
        """Remove and return an item from the queue.

        :raises RateLimitExceeded: If a token could not be consumed from the
            token bucket (consuming from the queue too fast).
        :raises Queue.Empty: If an item is not immediately available.

        Also see :meth:`Queue.Queue.get`.

        """
        get = block and self.queue.get or self.queue.get_nowait

        if not self.can_consume(1):
            raise RateLimitExceeded()

        return get()

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.

        :raises RateLimitExceeded: If a token could not be consumed from the
            token bucket (consuming from the queue too fast).
        :raises Queue.Empty: If an item is not immediately available.

        Also see :meth:`Queue.Queue.get_nowait`.

        """
        return self.get(block=False)

    def qsize(self):
        """Returns the size of the queue.

        See :meth:`Queue.Queue.qsize`.

        """
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()

    def clear(self):
        return self.items.clear()

    def wait(self, block=False):
        """Wait until a token can be retrieved from the bucket and return
        the next item."""
        while True:
            remaining = self.expected_time()
            if not remaining:
                return self.get(block=block)
            time.sleep(remaining)

    def can_consume(self, tokens=1):
        """Consume tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self._get_tokens():
            self._tokens -= tokens
            return True
        return False

    def expected_time(self, tokens=1):
        """Returns the expected time in seconds when a new token should be
        available."""
        tokens = max(tokens, self._get_tokens())
        return (tokens - self._get_tokens()) / self.fill_rate

    def _get_tokens(self):
        if self._tokens < self.capacity:
            now = time.time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self._tokens

    @property
    def items(self):
        return self.queue.queue
