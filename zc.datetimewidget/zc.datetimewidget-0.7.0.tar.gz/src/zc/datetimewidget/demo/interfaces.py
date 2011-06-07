from zope.interface import Interface
from zope.schema import Date, Datetime, Set


class IDemoContent(Interface):

    now = Datetime(title=u"Now", readonly=True)

    startDate = Date(title=u"Start Date")
    endDate = Date(title=u"End Date")

    startDatetime = Datetime(title=u"Start Datetime")
    endDatetime = Datetime(title=u"End Datetime")

    severalDates = Set(title=u"Several dates",
                       value_type=Date(title=u"Date"))
