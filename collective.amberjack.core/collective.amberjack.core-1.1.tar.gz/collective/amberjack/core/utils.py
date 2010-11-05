from zope.component import getUtility, getMultiAdapter
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.app.pagetemplate import engine

from collective.amberjack.core.validators import _validators_
from collective.amberjack.core.interfaces import IStep, IStepBlueprint, ITour, IAjConfiguration

from OFS.SimpleItem import SimpleItem

import ConfigParser
import re
import UserDict


def _load_config(configuration):
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = str # case sensitive
    parser.readfp(configuration)
    result = {}
    for section in parser.sections():
        result[section] = dict(parser.items(section))
    return result

def constructTour(tour, steps):
    results = []
    for step_id in steps:
        step_id = step_id.strip()
        if not step_id:
            continue
        step_options = tour[step_id]
        blueprint_id = step_options['blueprint'].decode('ascii')
        blueprint = getUtility(IStepBlueprint, blueprint_id)
        step = blueprint(tour, step_id, step_options)
        if not IStep.providedBy(step):
            raise ValueError('Blueprint %s for section %s did not return '
                             'an IStep' % (blueprint_id, step_id))
        results.append(step)
    return results


class Options(UserDict.DictMixin):
    def __init__(self, tour, step, data):
        self.tour = tour
        self.step = step
        self._raw = data
        self._cooked = {}
        self._data = {}

    def _substitute(self):
        for key, value in self._raw.items():
            if '${' in value:
                self._cooked[key] = self._sub(value, [(self.step, key)])
        
    def get(self, option, default=None, seen=None):
        try:
            return self._data[option]
        except KeyError:
            pass
        
        value = self._cooked.get(option)
        if value is None:
            value = self._raw.get(option)
            if value is None:
                return default
        
        if '${' in value:
            key = self.step, option
            if seen is None:
                seen = [key]
            elif key in seen:
                raise ValueError('Circular reference in substitutions.')
            else:
                seen.append(key)

            value = self._sub(value, seen)
            seen.pop()

        self._data[option] = value
        return value

    _template_split = re.compile('([$]{[^}]*})').split
    _valid = re.compile('\${[-a-zA-Z0-9 ._]+:[-a-zA-Z0-9 ._]+}$').match
    _tales = re.compile('^\s*string:', re.MULTILINE).match
    def _sub(self, template, seen):
        parts = self._template_split(template)
        subs = []
        for ref in parts[1::2]:
            if not self._valid(ref):
                 # A value with a string: TALES expression?
                if self._tales(template):
                    subs.append(ref)
                    continue
                raise ValueError('Not a valid substitution %s.' % ref)
            
            names = tuple(ref[2:-1].split(':'))
            value = self.tour[names[0]].get(names[1], None, seen)
            if value is None:
                raise KeyError('Referenced option does not exist:', *names)
            subs.append(value)
        subs.append('')

        return ''.join([''.join(v) for v in zip(parts[::2], subs)])
        
    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            pass

        v = self.get(key)
        if v is None:
            raise KeyError('Missing option: %s:%s' % (self.step, key))
        return v

    def __setitem__(self, option, value):
        if not isinstance(value, str):
            raise TypeError('Option values must be strings', value)
        self._data[option] = value

    def __delitem__(self, key):
        if key in self._raw:
            del self._raw[key]
            if key in self._data:
                del self._data[key]
            if key in self._cooked:
                del self._cooked[key]
        elif key in self._data:
            del self._data[key]
        else:
            raise KeyError, key

    def keys(self):
        raw = self._raw
        return list(self._raw) + [k for k in self._data if k not in raw]

    def copy(self):
        result = self._raw.copy()
        result.update(self._cooked)
        result.update(self._data)
        return result

class Condition(object):

    def __init__(self, expression, context, request):
        self.expression = expression
        self.context = context
        self.request = request

    def _get_globals(self):
        kw = {}
        for validator in _validators_:
          kw[validator.__name__] = validator
        kw['request'] = self.request
        kw['context'] = self.context
        return kw

    def __call__(self):
        _engine = engine.TrustedEngine
        _compiled = _engine.compile(self.expression)
        _globals = self._get_globals()
        _context = engine.TrustedEngine.getContext(_globals)
        return _compiled(_context)

class ToursRoot(object):
    implements(ITour)

    def getTourContext(self, context, path):
        site_root = '/'.join(context.portal_url.getPortalObject().getPhysicalPath())
        if not context.portal_amberjack.sandbox: 
            return context.unrestrictedTraverse(site_root + path)
        else:
            user_id = context.portal_membership.getAuthenticatedMember().id
            return context.unrestrictedTraverse(site_root + '/Members/' + user_id + path)
    
    def getToursRoot(self, context, request, url=''):
        portal_state =  getMultiAdapter((context, request), name=u'plone_portal_state')
        if url:
            if url.startswith('ABS'):
                return unicode(portal_state.navigation_root_url())
        if not context.portal_amberjack.sandbox:
            return unicode(portal_state.navigation_root_url())
        user_id = context.portal_membership.getAuthenticatedMember().id
        member_folder_path = '/Members/' + user_id
        try:
            portal_state.portal().restrictedTraverse(member_folder_path.split('/')[1:])
            return unicode(portal_state.navigation_root_url() + member_folder_path)
        except:
            return None
        
class AmberjackTool(SimpleItem):
    """Amberjack Tool"""
    implements(IAjConfiguration)
    
    sandbox = FieldProperty(IAjConfiguration['sandbox'])
    
