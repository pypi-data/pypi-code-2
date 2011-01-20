from os.path import basename, exists
from random import choice
from string import letters
from urllib import urlretrieve

from django.core.files import File
from django.db import models

class RandomManager():
    '''An abstract manager that adds a method to get  or create a random 
    instance of a model. Very useful for testing/features.'''
    def random_word(self, chars=10):
        '''Return a random string of a specific length.'''
        return "".join([choice(letters) for i in xrange(chars)])

    def random_text(self, words=20, chars=10):
        '''Return a random string of a specific length.'''
        return " ".join([self.random_word(chars) for i in xrange(words)])

    def get_or_create_random(self, **kwargs):
        """
        Returns an object with the given kwargs, selecting one at random if
        multiple exist, or creating one if necessary.
        """
        defaults = kwargs.pop('defaults', {})
        objects = self.filter(**kwargs).order_by('?')
        if objects:
            return objects[0]
        else:
            params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
            params.update(defaults)
            obj = self.model(**params)
            obj.save()
            return obj

