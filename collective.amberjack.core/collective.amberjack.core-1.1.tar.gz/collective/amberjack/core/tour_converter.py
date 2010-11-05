"""
migrates a dictionary-based tour into a configuration-based one
./bin/instance run src/collective.amberjack.core/collective/amberjack/core/tour_converter.py <tourId>

tourId is the one specified in the tour definition. e.g.
ajTour = {'tourId': u'basic01_add_and_publish_a_folder',
          'title': ...,
          'steps': ...
                   }
tourId can also be ALL that means "get all the registered tours and convert them"
"""
import sys
from zope.component import getUtility
from collective.amberjack.core.tour_manager import ITourManager
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
import ConfigParser

def normalize(noun):
    normalizer = getUtility(IIDNormalizer)
    return normalizer.normalize(noun)

class OrderedConfigParser(ConfigParser.RawConfigParser):

    def _ajcmp(self, x, y):
        x2=x.split('_')
        y2=y.split('_')
        xlen = len(x2)
        ylen = len(y2)
        if xlen > ylen:
            for i in range(xlen-ylen):
                y2.insert(-1, '')
        else:
            for i in range(ylen-xlen):
                x2.insert(-1, '')
        return cmp(x2, y2)

    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        keys = self._sections.keys()
        keys.sort(self._ajcmp)
        for section in keys:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items(): 
                if key != "__name__":
                    fp.write("%s = %s\n" %
                        (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")


class Converter:

    def __init__(self, tourId, tour):
        self.tourId = tourId
        self.tour = tour
        self.config = OrderedConfigParser()
        
    def convertTour(self):
        if not self.tour:
            return
        self.config.add_section('amberjack')
        self.config.set('amberjack', 'title', self.tour.__dict__['title'])

        section_steps = ['']
        for step_no, step in enumerate(self.tour.__dict__['steps']):
            step_name = self._step_name(step, step_no)
            section_steps.append(step_name)
            self.convert_step(step, step_no)

        self.set('amberjack', 'steps', section_steps)
        with open('%s.cfg' % self.tourId, 'wb') as configfile:
            self.config.write(configfile)

    def _step_name(self, step, step_no):
        return normalize('%s_%s' % (step_no, step['title']))

    def _microstep_name(self, step_no, i):
        return '%s_%s_microstep' % (step_no, i)

    def convert_step(self, step, step_no):
        step_name = self._step_name(step, step_no)
        self.config.add_section(step_name)
        self.config.set(step_name, 'blueprint', 'collective.amberjack.blueprints.step')
        for k, v in step.items(): 
            if k == 'validators':
                validators = ['']
                for validator in v:
                    validators.append(validator.__name__)
                self.set(step_name, 'validators', validators)
                continue
            if k == 'steps':
                section_microsteps = ['']
                for i, microstep in enumerate(v):
                    microstep_name = self._microstep_name(step_no, i)
                    section_microsteps.append(microstep_name)
                    self.convert_microstep(microstep, microstep_name)
                if section_microsteps != ['']:
                    self.set(step_name, 'microsteps', section_microsteps)
                continue

            self.set(step_name, k, v)

    def convert_microstep(self, microstep, microstep_name):
        self.config.add_section(microstep_name)
        self.config.set(microstep_name, 'blueprint', 'collective.amberjack.blueprints.microstep')
        for k, v in microstep.items():
            self.set(microstep_name, k, v)

    def set(self, section, k, v):
        if hasattr(v, '__iter__'):
            if ''.join(v).strip():
                self.config.set(section, k, '\n'.join(v))
        elif v.strip():
           self.config.set(section, k, v)

def main(app=None):
    tourId = sys.argv[1]
    manager = getUtility(ITourManager)
    if tourId == 'ALL':
        for tourId, tour in manager.getTours(app):
            Converter(tourId, tour).convertTour()
    else:
        tour = manager.getTour(tourId, app)
        Converter(tourId, tour).convertTour()

if __name__ == '__main__':
    main(app=app) 

