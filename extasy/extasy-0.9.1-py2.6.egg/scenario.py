#!/usr/bin/python
# -*- coding: utf8 -*-

import pyhistorian
import extasy

#overwrite _run_step method
def extasy__run_step(self, extasy_step, step_name):
    # @TODO: CHECK UNINDENT
    step = extasy_step[:-1]
    self.indentation_level = extasy_step[3]
    
    extasy.scope.quit_to_indentation_level( self.indentation_level )
    
    return pyhistorian__run_step( self, step, step_name )

pyhistorian__run_step = pyhistorian.Scenario._run_step
pyhistorian.Scenario._run_step = extasy__run_step


#overwrite run_steps method    
def extasy_run_steps(self, pyhistorian_steps, step_name):
    extasy_steps = getattr(self, '_extasy_%ss' % step_name)
    
    steps = []
    for i in xrange( len( pyhistorian_steps ) ):
        steps.append( pyhistorian_steps[ i ] + ( extasy_steps[i][3], ) )
    
    extasy.scope.reset()
    if len(steps) == 0:
        return
        
    self._run_step(steps[0], step_name)
    
    for step in steps[1:]:
        self._run_step(step, 'and')

pyhistorian_run_steps = pyhistorian.Scenario.run_steps
pyhistorian.Scenario.run_steps = extasy_run_steps