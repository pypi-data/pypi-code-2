"""
Serialize data to/from JSON
"""
from django.utils import simplejson
from python import Serializer as PythonSerializer
from django.core.serializers.json import Deserializer as JSONDeserializer, \
    DjangoJSONEncoder
from django.http import HttpResponse

class Serializer(PythonSerializer):
    """
    Convert a queryset to JSON.
    """
    def end_serialization(self):
        """Output a JSON encoded queryset."""
        self.options.pop('stream', None)
        self.options.pop('fields', None)
        self.options.pop('excludes', None)
        self.options.pop('relations', None)
        self.options.pop('extras', None)
        self.options.pop('use_natural_keys', None)
        self.use_httpresponse=self.options.pop('httpresponse', None)
        simplejson.dump(self.objects, self.stream, cls=DjangoJSONEncoder,
            **self.options)

    def getvalue(self):
        """
        Return the fully serialized queryset (or None if the output stream
        is not seekable).
        """

        if callable(getattr(self.stream, 'getvalue', None)):
            value = self.stream.getvalue()

        if self.use_httpresponse:
            return HttpResponse(value)
        else:
            return value

Deserializer = JSONDeserializer
