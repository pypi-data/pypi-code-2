from persistent import Persistent
from zope.interface import implements
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty
from interfaces import IDemoContent
from datetime import datetime
import pytz


class DemoContent(Persistent, Contained):

    implements(IDemoContent)

    startDate = FieldProperty(IDemoContent['startDate'])
    endDate = FieldProperty(IDemoContent['endDate'])

    startDatetime = FieldProperty(IDemoContent['startDatetime'])
    endDatetime = FieldProperty(IDemoContent['endDatetime'])

    severalDates = FieldProperty(IDemoContent['severalDates'])

    @property
    def now(self):
        return datetime.utcnow().replace(tzinfo=pytz.utc)
