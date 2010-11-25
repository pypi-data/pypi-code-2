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
                                ("0","Theories and Methods"),
                                ("1","Background"),
                                ("2","Crossroads"),
                                ("3","Models and Stereotypes"),
                                ("4","Europe on the Road"),
                                ("5","European Media"),
                                ("6","European Networks"),
                                ("7","Transnational Movements and Organizations"),
                                ("8","Alliances and Wars"),
                                ("9","Europe and the World"))

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