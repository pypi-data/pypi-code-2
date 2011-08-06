import logging, os, zc.buildout
import subprocess

class Dependencies(object):

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        for executable, system_package in [
                line.split(':') for line in options['bin'].split()]:
            print('Testing: ' + executable)
            try:
                assert(not subprocess.call(['which', executable], stdout=subprocess.PIPE))
                print('ok')
            except AssertionError:
                raise EnvironmentError('Your system is missing the following executable: '
                                       + executable
                                       + '. Please install ' + system_package)


    def install(self):
        pass

    def update(self):
        pass
