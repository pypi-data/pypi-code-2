# To change this template, choose Tools | Templates
# and open the template in the editor.

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

TOPICS = (("0","Education, Sciences"),
                                ("1", "Arts"),
		                ("2", "Social Matters, Society"),
		                ("3", "Politics"),
		                ("4", "Law, Constitution"),
		                ("5", "Religion"),
		                ("11", "Military"),
		                ("6", "Migration, Travel"),
		                ("7", "Media, Communication"),
		                ("8", "Agents, Intermediaries"),
		                ("9", "Theory, Methodology"),
				("10", "Economy, Technology"),)


class TopicsVocabulary(object):
    """
    Vocabulary for the topics
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, title) for value, title in TOPICS]
        return SimpleVocabulary(items)

TopicsVocabularyFactory = TopicsVocabulary()

AREA = (("1","Central Europe"),
				("0","Balkan Peninsula"),
				("5","Eastern Europe"),
				("2","Northern Europe"),
				("4","Western Europe"),
				("3","Southern Europe"),
				("6","Non-European World"))

class AreaVocabulary(object):
    """
    Vocabulary for the area
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, title) for value, title in AREA]
        return SimpleVocabulary(items)

AreaVocabularyFactory = AreaVocabulary()

THREAD = (("10", "Select All"),
                                ("Theories and Methods","Theories and Methods"),
                                ("Background","Background"),
                                ("Crossroads","Crossroads"),
                                ("Models and Stereotypes","Models and Stereotypes"),
                                ("Europe on the Road","Europe on the Road"),
                                ("European Media","European Media"),
                                ("European Networks","European Networks"),
                                ("Transnational Movements and Organizations","Transnational Movements and Organizations"),
                                ("Alliances and Wars","Alliances and Wars"),
                                ("Europe and the World","Europe and the World"))

class ThreadVocabulary(object):
    """
    Vocabulary for the thread
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, title) for value, title in THREAD]
        return SimpleVocabulary(items)

ThreadVocabularyFactory = ThreadVocabulary()

MEDIA = (("n","No Media Description"),
            ("a","Audio"),
            ("i", "Image"),
            ("v", "Video"),
            ("o", "Other"))

class MediaVocabulary(object):
    """
    Vocabulary for the media content
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, title) for value, title in MEDIA]
        return SimpleVocabulary(items)

MediaVocabularyFactory = MediaVocabulary()


TIMEFRAME = (("0", "before 1450"),
                ("1450", "1450 - 1459"),
                ("1460", "1460 - 1469"),
                ("1470", "1470 - 1479"),
                ("1480", "1480 - 1489"),
                ("1490", "1490 - 1499"),
                ("1500", "1500 - 1509"),
                ("1510", "1510 - 1519"),
                ("1520", "1520 - 1529"),
                ("1530", "1530 - 1539"),
                ("1540", "1540 - 1549"),
                ("1550", "1550 - 1559"),
                ("1560", "1560 - 1569"),
                ("1570", "1570 - 1579"),
                ("1580", "1580 - 1589"),
                ("1590", "1590 - 1599"),
                ("1600", "1600 - 1609"),
                ("1610", "1610 - 1619"),
                ("1620", "1620 - 1629"),
                ("1630", "1630 - 1639"),
                ("1640", "1640 - 1649"),
                ("1650", "1650 - 1659"),
                ("1660", "1660 - 1669"),
                ("1670", "1670 - 1679"),
                ("1680", "1680 - 1689"),
                ("1690", "1690 - 1699"),
                ("1700", "1700 - 1709"),
                ("1710", "1710 - 1719"),
                ("1720", "1720 - 1729"),
                ("1730", "1730 - 1739"),
                ("1740", "1740 - 1749"),
                ("1750", "1750 - 1759"),
                ("1760", "1760 - 1769"),
                ("1770", "1770 - 1779"),
                ("1780", "1780 - 1789"),
                ("1790", "1790 - 1799"),
                ("1800", "1800 - 1809"),
                ("1810", "1810 - 1819"),
                ("1820", "1820 - 1829"),
                ("1830", "1830 - 1839"),
                ("1840", "1840 - 1849"),
                ("1850", "1850 - 1859"),
                ("1860", "1860 - 1869"),
                ("1870", "1870 - 1879"),
                ("1880", "1880 - 1889"),
                ("1890", "1890 - 1899"),
                ("1900", "1900 - 1909"),
                ("1910", "1910 - 1919"),
                ("1920", "1920 - 1929"),
                ("1930", "1930 - 1939"),
                ("1940", "1940 - 1949"),
                ("1950", "1950 - 1959"),
                ("1960", "1960 - 1969"),
                ("1970", "1970 - 1979"),
                ("1980", "1980 - 1989"),
                ("1990", "1990 - 1999"),
                ("2000", "2000 - 2009"),
                ("2010", "2010 - 2019"))

class TimeframeVocabulary(object):
    """
    Vocabulary for the timeframe
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(value, title) for value, title in TIMEFRAME]
        return SimpleVocabulary(items)

TimeframeVocabularyFactory = TimeframeVocabulary()