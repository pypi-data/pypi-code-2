# -*- coding: utf-8 -*-
'''Provides a structure for input/output context with web server.'''

## Created: 2010-12-27 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

class InOut(object):
    """
    Provides a container object that holds context for input/output with the
    web server.
    """
    
    def __init__(self, environment=None):
        """
        Constructor.
        
        @param environment: WSGI server environment to initialise the container
            items.
        @type environment: C{dict}
        """
        
        self.output = None
        """Iterable content output holder. Ideally file like."""
        
        self.content_length = 0
        """Content length in bytes of serialised content of output (C{int})."""
        
        self.response_headers = [('Content-type', 'text/plain')]
        """C{list} of tuples (C{str}, C{str})of for the HTTP header response
           (default: set for plain text)."""
        
        self.input_stream = None
        """WSGI input data stream for receiving bulk content."""
        
        self.output_stream_factory = None
        """
        WSGI output data stream generator function for returning bulk content.
        Takes the C{data} (file like object, "pay load") and C{block_size} as
        arguments, with the C{block_size} being optional.
        """
        
        if 'wsgi.input' in environment:
            self.input_stream = environment['wsgi.input']
        
        if 'wsgi.file_wrapper' in environment:
            self.output_stream_factory = environment['wsgi.file_wrapper']
    
    
    def set_output_stream(self, data, block_size=None):
        """
        Assigns the output stream L{output} of the object to use for the
        response with the parameter C{data}, using the WSGI C{file_wrapper}.
        The C{file_wrapper} can be specified with an optional C{block_size} for
        the output.
        
        @param data: Data object to use for linking to the output stream.
        @type data: "File like" object.
        @param block_size: Size of blocks to use for transfer.
        @type block_size: C{int}
        """
        if self.output_stream_factory:
            self.output = self.output_stream_factory(data, block_size)
        else:
            # We don't have a WSGI file_wrapper, so let's go traditional.
            self.output = data
