from zope.interface import implements
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from collective.amberjack.core.interfaces import ITour
from collective.amberjack.core import utils

import UserDict
from collective.amberjack.core.validators import AmberjackException
from zope.i18nmessageid import MessageFactory
import os

class Tour(UserDict.DictMixin):
    implements(ITour)

    def __init__(self, configuration, tour_id):
        try:
            self._filename = os.path.basename(configuration.name)
        except AttributeError:
            self._filename = 'no_filename'
        domain = os.path.splitext(os.path.basename(self._filename))[0]
        self.mf = MessageFactory(domain)
        self._raw = utils._load_config(configuration)
        self._data = {}
        self._options = self._raw['amberjack']
        self._steps_ids = self._options['steps'].splitlines()
        self.steps = utils.constructTour(self, self._steps_ids)
        self.title = self.mf(u'amberjack_title', default=self._options['title'])
        self.validators = self._options.get('validators','').splitlines()
        self.setTourId()

    def setTourId(self):
        normalizer = getUtility(IIDNormalizer)
        self.tourId = normalizer.normalize('%s.%s' % (os.path.splitext(self._filename)[0], self._options['title']))

    def validate(self, context, request):
        errors = []
        for expression in self.validators:
            if not expression:
                continue
            rootTool = getUtility(ITour, 'collective.amberjack.core.toursroot')
            path = [s.url for s in self.steps if s.url!='aj_any_url'][0]
            condition = utils.Condition(expression, rootTool.getTourContext(context, path), request)
            try:
                message = condition()
                message #pyflakes
            except AmberjackException, e:
                errors.append(str(e))
        return errors

    def __getitem__(self, step):
        try:
            return self._data[step]
        except KeyError:
            pass
        data = self._raw[step]
        options = utils.Options(self, step, data)
        self._data[step] = options
        options._substitute()
        return options

    def __setitem__(self, key, value):
        raise NotImplementedError('__setitem__')

    def __delitem__(self, key):
        raise NotImplementedError('__delitem__')

    def keys(self):
        return self._raw.keys()

    def __repr__(self):
        return ('<AmberjackTour based on %s>' % self._filename)
