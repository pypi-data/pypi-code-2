#!/usr/bin/python
# -*- coding: utf8 -*-

import pyhistorian
import extasy
import re

#overwrite _run_step method
def extasy__run_step(self, extasy_step, step_name):
    # @TODO: CHECK UNINDENT
    step = extasy_step[:-1]
    self.indentation_level = extasy_step[3]
    
    extasy.scope.quit_to_indentation_level( self.indentation_level )
    
    method, message_template, args = step
    message = re.sub( r'\$([a-zA-Z]\w+)', r'%(\1)s', message_template.replace( '%', '%%' ) ) % args
    if hasattr(method, 'pending'):
        self._pendings.append(method)
        self._output_writer.output_pending_step_line(step_name,
                                                     message,
                                                     self._pending_color)
        return
    try:        
        self._output_writer._stream.write( self._output_writer._colored( '    %s %s   ...' % ( self._language[step_name].capitalize(), message), 'white' ) )
        
        method(self, **args)
        
        self._output_writer._stream.write( self._output_writer._colored( '\r', 'white' ) )
        self._output_writer.output_ok_step_line(step_name,
                                                message,
                                                'green')
    except AssertionError, e:
        self._failures.append(self._get_traceback_info())
        self._output_writer._stream.write( self._output_writer._colored( '\r', 'white' ) )
        self._output_writer.output_fail_step_line(step_name,
                                                 message,
                                                 self._failure_color)
    except Exception, e:
        self._errors.append(self._get_traceback_info())
        self._output_writer._stream.write( self._output_writer._colored( '\r', 'white' ) )
        self._output_writer.output_error_step_line(step_name,
                                                   message,
                                                   self._error_color)

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