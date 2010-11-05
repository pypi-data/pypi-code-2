from zope.interface import classProvides, implements
from zope.component import getUtility
from collective.amberjack.core.interfaces import IStep, IStepBlueprint
from collective.amberjack.core.utils import Condition

SSPAN = '<span class="ajHighlight">'
ESPAN = '</span>'

class Step(object):
    classProvides(IStepBlueprint)
    implements(IStep)
    
    def __init__(self, tour, name, options):
        self._tour = tour
        self._options = options        
        self.microsteps = self.constructMicroSteps(options)
        
        self.xpath = self._options.get('xpath','')
        self.xcontent = self._options.get('xcontent','')
        self.url = self._options['url']
        self.title = tour.mf(u'%s_title' % name, self._options['title'])
        self.text = tour.mf(u'%s_text' % name, normalizeHTML(self._options.get('text','')))
        self.validators = self._options.get('validators','').splitlines()

    def constructMicroSteps(self, options):
        microsteps = options.get('microsteps','').splitlines()
        results = []
        for microstep_id in microsteps:
            microstep_id = microstep_id.strip()
            if not microstep_id:
                continue
            microstep_options = self._tour[microstep_id]
            blueprint_id = microstep_options['blueprint'].decode('ascii')
            blueprint = getUtility(IStepBlueprint, blueprint_id)
            microstep = blueprint(self._tour, microstep_id, microstep_options)
            if not IStep.providedBy(microstep):
                raise ValueError('Blueprint %s for section %s did not return '
                                 'an IStep' % (blueprint_id, microstep_id))
            results.append(microstep)
        return results

    def validate(self, context, request):
        errors = []
        for expression in self.validators:
            if not expression:
                continue
            condition = Condition(expression, context, request)
            message = condition()
            if message:
                errors.append(message)
        return errors

class MicroStep(object):
    classProvides(IStepBlueprint)
    implements(IStep)
    
    def __init__(self, tour, name, options):
        self._tour = tour
        self._options = options
        self.description = tour.mf(u'%s_description' % name, normalizeHTML(self._options['description']))
        self.selector = self._options.get('selector','')
        self.text = tour.mf(u'%s_text' % name, normalizeHTML(self._options.get('text','')))
        self.method=self._options.get('method','')

 
"""
Windmill microstep
"""     
class WindmillMicroStep(object):
    classProvides(IStepBlueprint)
    implements(IStep)
    
    def __init__(self, tour, name, options):
        self._tour = tour
        self._options = options
        self.description = tour.mf(u'%s_description' % name, normalizeHTML(self._options['description']))
        self.selector = self._options.get('selector','')
        self.method=self._options.get('method','')
        self.text = tour.mf(u'%s_text' % name, normalizeHTML(self._options.get('text','')))
        self.required=self._options.get('required','')
        self.condition=self._options.get('condition','')


def normalizeHTML(text):
    return text.replace('[', SSPAN).replace(']', ESPAN)
