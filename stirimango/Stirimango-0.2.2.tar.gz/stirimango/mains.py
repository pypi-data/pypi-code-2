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


'''The complete stirimango codebase resides in this single package with no
submodules or subpackages.

More mature releases may support other RDBMS using subpackages.
'''


__all__ = ['main_init', 'main_list', 'main_status', 'main_forward',
        'main_backward']


import getopt
import getpass
import os

import postgresql.driver

from stirimango import actions
from stirimango import exceptions


DATABASE_GETOPT_SHORT = 'd:h:p:U:Ws:'
DATABASE_GETOPT_LONG = ['dbname=', 'host=', 'port=', 'username=', 'password',
        'schema=']


def connect_to_database(optlist):
    '''Use the options list (from getopt) to connect to the database.
    '''
    options = {}
    password = False
    for flag, value in optlist:
        if flag in ('-d', '--dbname'):
            options['database'] = value
        elif flag in ('-h', '--host'):
            options['host'] = value
        elif flag in ('-p', '--port'):
            options['port'] = value
        elif flag in ('-U', '--username'):
            options['user'] = value
        elif flag in ('-W', '--password'):
            password = True
    if password:
        options['password'] = getpass.getpass()
    return postgresql.open(**options)


def get_option(optlist, *args):
    '''Parse the value from args.

    The last flag in oplist that matches will be returned (or None, if none
    match).

    .. doctest::

       >>> get_option([('-s', 'schema')], '-s', '--schema')
       'schema'
       >>> get_option([('--schema', 'schema')], '-s', '--schema')
       'schema'
       >>> get_option([('--empty', '')], '-s', '--schema')
    '''
    ret = None
    for flag, value in optlist:
        if flag in args:
            ret = value
    return ret


def main_init(argv, stdout=None, stderr=None):
    '''The main function for :func:`actions.action_init`.

    :func:`main_init` parses argv and calls :func:`actions.action_init`.
    '''
    try:
        optlist, args = getopt.getopt(argv, DATABASE_GETOPT_SHORT,
                DATABASE_GETOPT_LONG)
        if len(args) != 0:
            raise exceptions.Usage(_('Extraneous arguments provided.'))
        connection = connect_to_database(optlist)
        schema = get_option(optlist, '-s', '--schema')
        actions.action_init(connection, schema, stdout, stderr)
        return 0
    except ( exceptions.AlreadyInitialized
           , exceptions.UnknownSchema
           , exceptions.Usage
           ) as ex:
        print(ex.msg, file=stderr)
        return 2


def main_list(argv, stdout=None, stderr=None):
    '''The main function for :func:`actions.action_list`.

    :func:`main_list` parses argv and calls :func:`actions.action_list`.

    In the typical case, the argument will simply be passed through to
    :func:`actions.action_list`.

    .. doctest::

       >>> ret = main_list(['testdata.sample'])
       2010-07-04T00:00:00_create_products_table
       <BLANKLINE>
           Create a table to hold products for sale.
       <BLANKLINE>
       2010-07-05T00:05:00_products_add_description_column
       <BLANKLINE>
           Add a column for describing the products to customers.
       <BLANKLINE>
       2010-07-05T00:05:50_no_description
       <BLANKLINE>
       2010-07-06T00:00:00_products_remove_description_column
       <BLANKLINE>
           Remove the `description` column in the `products` table.
       <BLANKLINE>
           The product descriptions will be stored somewhere else.
        >>> ret
        0

    If the user provides improper arguments, then the return value will be
    non-zero and an error message will be reported.

    .. doctest::

       >>> ret = main_list([])
       Provide the name of a single migrations package.
       >>> ret
       2
       >>> ret = main_list(['testdata.nonpackage'])
       The package specified is not a stirimango migrations package.
       >>> ret
       2
    '''
    try:
        if len(argv) != 1:
            error = _('Provide the name of a single migrations package.')
            raise exceptions.Usage(error)
        actions.action_list(argv[0], stdout, stderr)
        return 0
    except (exceptions.InvalidPackage, exceptions.Usage) as ex:
        print(ex.msg, file=stderr)
        return 2


def main_status(argv, stdout=None, stderr=None):
    '''The main function for :func:`actions.action_status`.

    :func:`main_status` parses argv and calls :func:`actions.action_status`.
    '''
    try:
        optlist, args = getopt.getopt(argv, DATABASE_GETOPT_SHORT,
                DATABASE_GETOPT_LONG)
        if len(args) != 1:
            error = _('Provide the name of a single migrations package.')
            raise exceptions.Usage(error)
        connection = connect_to_database(optlist)
        schema = get_option(optlist, '-s', '--schema')
        actions.action_status(args[0], connection, schema, stdout, stderr)
        return 0
    except ( exceptions.UnknownSchema
            , exceptions.Usage
           ) as ex:
        print(ex.msg, file=stderr)
        return 2


def main_migrate(action, argv, stdout=None, stderr=None):
    '''A shared main function for migration.
    '''
    try:
        optlist, args = getopt.getopt(argv, DATABASE_GETOPT_SHORT + 'n:u:',
                DATABASE_GETOPT_LONG + ['number=', 'one='])
        if len(args) != 1:
            error = _('Provide the name of a single migrations package.')
            raise exceptions.Usage(error)
        connection = connect_to_database(optlist)
        schema = get_option(optlist, '-s', '--schema')
        number = get_option(optlist, '-n', '--number')
        until = get_option(optlist, '-u', '--until')
        if number:
            try:
                number = int(number)
            except ValueError as ex:
                raise exceptions.Usage(_('-n/--number needs an integer'))
        action(args[0], connection, number, until, schema, stdout, stderr)
        return 0
    except ( exceptions.UnknownSchema
            , exceptions.Usage
           ) as ex:
        print(ex.msg, file=stderr)
        return 2


def main_forward(argv, stdout=None, stderr=None):
    '''The main function for :func:`actions.action_forward`.

    :func:`main_forward` parses argv and calls :func:`actions.action_forward`.
    '''
    return main_migrate(actions.action_forward, argv, stdout, stderr)


def main_backward(argv, stdout=None, stderr=None):
    '''The main function for :func:`actions.action_backward`.

    :func:`main_backward` parses argv and calls :func:`actions.action_backward`.
    '''
    return main_migrate(actions.action_backward, argv, stdout, stderr)
