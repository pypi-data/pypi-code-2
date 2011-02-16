import json
import functools
from datetime import datetime
from mongoengine import (Document, EmbeddedDocument, ListField, StringField,
    GenericReferenceField, EmbeddedDocumentField, DictField, DateTimeField)
from pymongo.errors import ConnectionFailure


def atomic(f):
    """
    Transforms the given function into an atomic operation. The function
    itself should be idempotent, that is repeatable without harm.

    >>> class Foo(mongoengine.Document):
    ...     @atomic
    ...     def bar(self):
    ...         # Do shit.
    ...         return "stuff"
    """
    @functools.wraps(f)
    def wrapper(instance, *args, **kwargs):
        with Operation(instance, f.func_name, *args, **kwargs):
            return f(instance, *args, **kwargs)
    wrapper.recover = f
    return wrapper


class ReferenceMapping(EmbeddedDocument):
    """
    A key-value mapping. The key is a short string. The value is a reference
    to a :class:`mongoengine.Document`\.
    """
    key = StringField(max_length=20, required=True)
    value = GenericReferenceField()


class OperationLog(Document):
    """
    A log of a operation. This stores information about a method call on
    :class:`mongoengine.Document`\s.
    """
    instance = GenericReferenceField(required=True)
    method = StringField(max_length=100)
    arg_references = ListField(EmbeddedDocumentField(ReferenceMapping),
        default=[])
    arg_others = DictField(default={})
    kwarg_references = ListField(EmbeddedDocumentField(ReferenceMapping),
        default=[])
    kwarg_others = DictField(default={})
    timestamp = DateTimeField(default=datetime.now)

    def __getattr__(self, name):
        if name == 'args':
            return self.to_args()
        if name == 'kwargs':
            return self.to_kwargs()
        return super(OperationLog, self).__getattr__(name)

    def recover(self):
        """
        Recovers the log.
        """
        # Fetch the method via its method name.
        method = getattr(self.instance, self.method)
        # Run the recovery. i.e. the original function without
        # the context management.
        # see the decorator atomic
        return method.recover(self.instance, *self.args, **self.kwargs)

    @classmethod
    def recover_all(cls):
        """
        Runs recovery on all interrupted operations.
        """
        for log in OperationLog.objects.order_by('timestamp'):
            log.recover()
            log.delete(safe=True)
            # XXX exception handling?

    @classmethod
    def create(cls, op):
        """
        :param op: The :class:`Operation` instance.
        :returns: A :class:`OperationLog` from the given :class:`Operation`\.
        """
        arg_refs, arg_others = cls.from_args(op.args)
        kwarg_refs, kwarg_others = cls.from_kwargs(op.kwargs)
        op_log = cls(instance=op.instance, method=op.method)
        op_log.arg_references = arg_refs
        op_log.arg_others = arg_others
        op_log.kwarg_references = kwarg_refs
        op_log.kwarg_others = kwarg_others
        return op_log

    @classmethod
    def from_args(cls, args):
        """
        :param args: The list of arguments passed to the function.
        :returns: A tuple of a list of :class:`ReferenceMapping`\s and
            the other arguments.
        """
        def _gen():
            for index, item in enumerate(args):
                yield str(index), item
        return cls.from_kwargs(dict(_gen()))

    def to_args(self):
        """
        :returns: The original list or arguments.
        """
        args = [None] * (len(self.arg_references) + len(self.arg_others))
        for x in self.arg_references:
            args[int(x.key)] = x.value
        for k, v in self.arg_others.items():
            args[int(k)] = json.loads(v)
        return args

    @classmethod
    def from_kwargs(cls, kwargs):
        """
        :param kwargs: A `dict`.
        :returns: A tuple of a list of :class:`ReferenceMapping`\s and
            the other arguments.
        """
        references = []
        others = {}
        for k, v in kwargs.items():
            if isinstance(v, Document):
                references.append(ReferenceMapping(key=k, value=v))
            else:
                others[k] = json.dumps(v)
        return references, others

    def to_kwargs(self):
        """
        :returns: The original dict of keyword arguments.
        """
        kwargs = {}
        for x in self.kwarg_references:
            kwargs[x.key] = x.value
        for k, v in self.kwarg_others.items():
            kwargs[k] = json.loads(v)
        return kwargs


class Operation(object):

    def __init__(self, instance, method, *args, **kwargs):
        self.instance = instance
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.log = None

    def __enter__(self):
        self.log = OperationLog.create(self)
        self.log.save(safe=True)

    def __exit__(self, type, value, traceback):
        # If there was an exception raised and if it was a ConnectionFailure,
        # the log is preserved.
        if value is not None and isinstance(value, ConnectionFailure):
            return False
        self.log.delete(safe=True)
