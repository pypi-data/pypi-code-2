# Copyright (c) 2010, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Stirimango nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


'''Exceptions used for Stirimango error conditions.
'''


class StirimangoException(Exception):
    '''All stirimango exceptions inherit from this class.

    .. doctest::

       >>> raise StirimangoException('sample error message')
       Traceback (most recent call last):
       stirimango.exceptions.StirimangoException: sample error message

    The default message is the docstring.

    .. doctest::

       >>> raise StirimangoException() #doctest: +ELLIPSIS
       Traceback (most recent call last):
       stirimango.exceptions.StirimangoException: All stirimango exceptions ...
       ...
    '''

    def __init__(self, msg=None):
        msg = msg or self.__doc__
        super(StirimangoException, self).__init__(msg)
        self.msg = msg


class InvalidPackage(StirimangoException):
    '''The package specified is not a stirimango migrations package.'''


class AlreadyInitialized(StirimangoException):
    '''The database/schema is already initialized.'''


class NotInitialized(StirimangoException):
    '''The database/schema is not initialized.'''


class UnknownSchema(StirimangoException):
    '''No such schema exists.'''


class Usage(StirimangoException):
    '''A user-initiated action or input has caused an exception.'''
