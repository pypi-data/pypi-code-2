from zope.schema import vocabulary
import interfaces
from Products.CMFCore.utils import getToolByName
from zope.i18nmessageid import MessageFactory
from Solgema.fullcalendar.config import _
PLMF = MessageFactory('plonelocales')

class TitledVocabulary(vocabulary.SimpleVocabulary):
    def fromTitles(cls, items, *interfaces):
        terms = [cls.createTerm(value,value,title) for (value,title) in items]
        return cls(terms, *interfaces)
    fromTitles = classmethod(fromTitles)

def availableViews( context ):
    voc = [('month', _('Month', default='Month')),
           ('basicWeek', _('basicWeek', default='basicWeek')),
           ('basicDay', _('basicDay', default='basicDay')),
           ('agendaWeek', _('agendaWeek', default='agendaWeek')),
           ('agendaDay', _('agendaDay', default='agendaDay'))
          ]
    return TitledVocabulary.fromTitles( voc )

def daysOfWeek( context ):
    ts = getToolByName(context, 'translation_service')
    return TitledVocabulary.fromTitles([(d, PLMF(ts.day_msgid(d), default=ts.weekday_english(d))) for d in range(6)])

def dayHours( context ):
    return TitledVocabulary.fromTitles([(a, a<10 and '0'+str(a)+':00' or str(a)+':00') for a in range(25)])

def availableCriterias( topic ):
    li = []
    portal_atct = getToolByName(topic, 'portal_atct')
    for criteria in topic.listCriteria():
        field = criteria.Field()
        if criteria.meta_type=='ATPortalTypeCriterion' and len(criteria.getCriteriaItems()[0][1])>1:
            index = portal_atct.getIndex(field).friendlyName or ortal_atct.getIndex(field).index
            li.append({'id':field, 'title':topic.translate(index)})
        elif criteria.meta_type in ['ATSelectionCriterion', 'ATListCriterion'] and len(criteria.getCriteriaItems()[0][1]['query'])>1:
            index = portal_atct.getIndex(field).friendlyName or ortal_atct.getIndex(field).index
            li.append({'id':field, 'title':topic.translate(index)})
    return TitledVocabulary.fromTitles([(crit['id'], crit['title']) for crit in li])
