#!/usr/bin/env python
'''
sweety.process

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''

import logging
import os
from subprocess import Popen, PIPE

from sweety.log import get_logger

class Command(object):
        '''
        Represents an executable command.
        '''

        def __init__(self, cmd, env = {}, cwd = None):
                '''
                Initializes a new Command object.
                
                @param cmd: the command to be executed.
                @param env: the environment variables.
                @param cwd: the working directory.
                '''
                self.cmd = cmd
                if not env:
                        env = os.environ
                self.env = env
                self.last_returncode = None
                self.last_result = []
                self.cwd = cwd

                self._log = get_logger(self)
                self._filelog = None
                for h in self._log.handlers:
                        if isinstance(h, logging.FileHandler):
                                self._filelog = h
                                break


        def call(self, show_output = False, output_template = '%s', log_error = True):
                '''
                call(self, show_output = False, output_template = '%s') -> return code
                
                Executes the command.
                
                @param show_output indicates whether display command output at the console.
                @param output_template: the string template used to format each line of the output content.
                @param log_error: indicates whether logs the stderr output.
                @return: the return code.
                '''
                self.last_result = []
                self.last_returncode = None

                if log_error and self._filelog:
                        errfd = self._filelog.stream
#               elif log_error:
#                       errfd = None
                else:
                        errfd = open('/dev/null', 'w')

                self._log.debug('Command=[%s].' % ' '.join(self.cmd.split()))

                try:
                        p = Popen(self.cmd, stdout = PIPE, shell = True, env = self.env, cwd = self.cwd, stderr = errfd)
                except:
                        self._log.warning('Failed to execute command [%s].' % self.cmd)

                        return None

                if show_output and p.stdout:
                        for l in p.stdout:
                                l = l.rstrip('\n\r')
                                self.last_result.append(l)
                                self._log.info(output_template % l)
                elif p.stdout:
                        for l in p.stdout:
                                l = l.rstrip('\n\r')
                                self.last_result.append(l)
                                self._log.debug(output_template % l)

                p.wait()

                self.last_returncode = p.returncode

                self._log.debug('returncode=[%d].' % self.last_returncode)

                #if p.returncode:
                #       self._log.warning('Failed to execute command [%s], status code %d.' % (self.cmd, p.returncode))

                        #return p.returncode

                return p.returncode


        def flush_call(self, input = '', show_output = False, output_template = '%s', log_error = True):
                '''
                flush_call(self, input = '', sow_output = False, output_template = '%s') -> return code
                
                Executes the command, and pass the input content to the command via standard input.
                
                @param input: specified the input content.
                @param show_output: indicates whether display command output at the console.
                @param output_template: the string template used to format echo line of the output content.
                @param log_error: indicates whether logs the stderr output.
                @return: the return code.
                '''
                self.last_result = []
                self.last_returncode = None

                if log_error and self._filelog:
                        errfd = self._filelog.stream
#               elif log_error:
#                       errfd = None
                else:
                        errfd = open('/dev/null', 'w')

                self._log.info('Input=[%s]' % input)
                self._log.info('Command=[%s]' % self.cmd)

                e = Popen(['echo', input], stdout = PIPE)
                try:
                        p = Popen(self.cmd, stdin = e.stdout, stdout = PIPE, shell = True, env = self.env, cwd = self.cwd, stderr = errfd)
                except:
                        self._log.warning('Failed to execute command [%s].' % self.cmd)

                        return None

                if show_output and p.stdout:
                        for l in p.stdout:
                                l = l.rstrip('\n\r')
                                self.last_result.append(l)
                                self._log.info(output_template % l)
                elif p.stdout:
                        for l in p.stdout:
                                l = l.rstrip('\n\r')
                                self.last_result.append(l)
                                self._log.debug(output_template % l)

                e.wait()
                p.wait()

                self.last_returncode = p.returncode

                self._log.info('returncode=[%d].' % self.last_returncode)

                #if p.returncode:
                #       self._log.warning('Failed to execute command [%s] with input [%s], status code %d.' % (self.cmd, input, p.returncode))


                return p.returncode


        def get_result_table(self):
                '''
                get_result_table(self) -> list of list
                
                Gets the last result in table-style.
                '''
                return [l.split('\t') for l in self.last_result]


        def get_result_string(self, join = '\n'):
                '''
                get_result_string(self) -> string
                
                Gets the last result in a single string.
                '''
                return join.join(self.last_result)

