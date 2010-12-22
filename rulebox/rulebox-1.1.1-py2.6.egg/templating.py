# -*- coding: utf-8 -*-
# This file is part of Rulebox.
# Rulebox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Rulebox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008-2010 Brandon Evans and Chris Santiago.
# http://www.suitframework.com/
# http://www.suitframework.com/docs/credits

"""A set of rules used to transfer information from the code to the template in
order to create an HTML document.

-----------------------------
Example Usage
-----------------------------

::

    import suit # easy_install suit
    from rulebox import templating
    template = open('template.tpl').read()
    # Template contains "Hello, <strong>[var]username[/var]</strong>!"
    templating.var.username = 'Brandon'
    print suit.execute(templating.rules, template)
    # Result: Hello, <strong>Brandon</strong>!

Basic usage; see http://www.suitframework.com/docs/ for how to use other rules.

-----------------------------
Var and Rules
-----------------------------

``var``
    obj - Container of variables to be used in with various rules.

``rules``
    dict - Contains the rules for the Templating Ruleset.
"""

import copy
import os
import re
import cgi
try:
    import json
except ImportError:
    import simplejson as json

from markupsafe import Markup
import suit

__all__ = [
    'assign', 'attribute', 'bracket', 'Class', 'comments', 'condition',
    'decode', 'default', 'entities', 'execute', 'getvariable', 'listing',
    'loadlocal', 'loop', 'loopiteration', 'returning', 'rules', 'savelocal',
    'setvariable', 'templates', 'trim', 'trying', 'variables', 'walk'
]

class Class():
    """Just an empty object."""
    pass

var = Class()

def assign(params):
    """Assign variable in the template."""
    # If a variable is provided.
    if 'var' in params['var']:
        if params['var']['json']:
            params['string'] = json.loads(params['string'])
        setvariable(
            params['var']['var'],
            params['var']['delimiter'],
            params['string'],
            params['var']['owner']
        )
    params['string'] = ''
    return params

def attribute(params):
    """Create rule out of attributes."""
    variable = params['rules'][params['tree']['rule']]['var'].copy()
    params['var'] = variable['var'].copy()
    # Decide where to get the attributes from.
    if 'onesided' in variable and variable['onesided']:
        string = params['string']
    elif 'create' in params['tree']:
        string = params['tree']['create']
    else:
        return params
    quote = ''
    smallest = False
    # Decide which quote string to use based on which occurs first.
    for value in variable['quote']:
        haystack = string
        needle = value
        if params['config']['insensitive']:
            haystack = haystack.lower()
            needle = needle.lower()
        position = haystack.find(needle)
        if position != -1 and (smallest == False or position < smallest):
            quote = value
            smallest = position
    if quote:
        # Split up the string by quotes.
        split = string.split(quote)
        del split[-1]
        for key, value in enumerate(split):
            # If this is the opening quote.
            if key % 2 == 0:
                name = value.strip()
                syntax = (
                    name[
                        len(name) - len(variable['equal'])
                    ] == variable['equal']
                )
                name = name[0:len(name) - len(variable['equal'])]
                # If the syntax is not valid or the variable is not whitelisted
                # or blacklisted, do not prepare to define the variable.
                if not syntax or not listing(name, variable):
                    name = ''
            elif name:
                # Define the variable.
                config = params['config'].copy()
                config['log'] = variable['log']
                params['var'][name] = suit.execute(
                    params['rules'],
                    value,
                    config
                )
    return params

def bracket(params):
    """Handle brackets unrelated to the rules."""
    params['string'] = ''.join((
        params['tree']['rule'],
        params['string'],
        params['rules'][params['tree']['rule']]['close']
    ))
    return params

def condition(params):
    """Show the string if necessary."""
    # Do not show if no condition provided.
    if not 'condition' in params['var']:
        return params
    variable = getvariable(
        params['var']['condition'],
        params['var']['delimiter'],
        params['var']['owner']
    )
    # Show the string if the condition is true.
    if (
        (
            variable and
            not params['var']['not']
        ) or
        (
            not variable and
            params['var']['not']
        )
    ):
        params = walk(params)
    return params

def copyvar(params):
    """Copy the rule's variable from the tree."""
    params['var'] = params['rules'][params['tree']['rule']]['var'].copy()
    return params

def decode(params):
    """Decode a JSON String."""
    params['var'] = params['var'].copy()
    for value in params['var']['decode']:
        params['var'][value] = json.loads(params['var'][value])
    return params

def entities(params):
    """Convert HTML characters to their respective entities."""
    if not params['var']['json'] and params['var']['entities']:
        params['string'] = cgi.escape(Markup(params['string']).unescape())
    return params

def execute(params):
    """Execute the string using the same rules used in this template."""
    config = params['config'].copy()
    config['log'] = params['var']['log']
    params['string'] = suit.execute(
        params['rules'],
        params['string'],
        config
    )
    return params

def functions(params):
    """Perform a function call."""
    # If the node using this is one sided, make the string empty by default.
    if 'onesided' in params['var'] and params['var']['onesided']:
        params['string'] = ''
    # If a function was provided.
    if params['var']['function'] and params['var']['owner']:
        function = getvariable(
            params['var']['function'],
            params['var']['delimiter'],
            params['var']['owner']
        )
        kwargs = {}
        for index, value in params['var'].items():
            kwargs[str(index)] = value
        # Remove the parameters that shouldn't be used in the call.
        del kwargs['delimiter']
        del kwargs['function']
        del kwargs['owner']
        params['string'] = function(**kwargs)
    return params

def getvariable(string, split, owner):
    """Get a variable based on a split string.

    ``string``
        str - The name of the variable to grab.

    ``split``
        str - The string that separates the levels of the variable.

    ``owner``
        mixed - The object to grab the variable from.

    Returns: mixed - The variable.
    """
    for value in string.split(split):
        try:
            owner = owner[value]
        except (AttributeError, TypeError):
            try:
                owner = owner[int(value)]
            except (AttributeError, TypeError, ValueError):
                owner = getattr(owner, value)
    return owner

def iterate(iterable):
    """Iterate over any object.

    ``iterable``
        mixed - The object to iterate over.

    Returns: mixed - The items in key, value format.
    """
    if hasattr(iterable, 'items'):
        iterations = list(iterable.items())
    else:
        try:
            iterations = enumerate(iterable)
        except (TypeError, RuntimeError):
            iterations = []
            for value in dir(iterable):
                if (
                    not value.startswith('_') and
                    not callable(getattr(iterable, value))
                ):
                    iterations.append((
                        value,
                        getattr(iterable, value)
                    ))
    return iterations

def listing(name, variable):
    """Check if the variable is whitelisted or blacklisted and determine
    whether or not the variable can be used.

    ``name``
        str - The name of the variable to check.

    ``variable``
        dict - A dict containing the `list` and `blacklist` keys if applicable.

    Returns: bool - Whether or not the variable can be used.
    """
    return not (
        'list' in variable and
        (
            (
                (
                    not 'blacklist' in variable or
                    not variable['blacklist']
                ) and
                not name in variable['list']
            ) or
            (
                'blacklist' in variable and
                variable['blacklist'] and
                name in variable['list']
            )
        )
    )

def loadlocal(params):
    """Reset the variables set before this section."""
    # Set the variables.
    for key, value in list(params['var']['local'].items()):
        if hasattr(params['var']['owner'], 'items'):
            params['var']['owner'][key] = value
        else:
            try:
                params['var']['owner'][int(key)] = value
            except (AttributeError, TypeError, ValueError):
                setattr(
                    params['var']['owner'],
                    key,
                    value
                )
    # Remove the variables set after this section.
    if hasattr(params['var']['owner'], 'items'):
        for key, value in list(params['var']['owner'].items()):
            if not key in params['var']['local']:
                del params['var']['owner'][key]
    else:
        try:
            for key, value in enumerate(params['var']['owner']):
                if key >= len(params['var']['local']) - 1:
                    del params['var']['owner'][key]
        except (TypeError, RuntimeError):
            for value in dir(params['var']['owner']):
                if (
                    not value.startswith('_') and
                    not callable(getattr(params['var']['owner'], value))
                ):
                    if not value in params['var']['local']:
                        delattr(
                            params['var']['owner'],
                            value
                        )
    return params

def loop(params):
    """Loop a string with different variables."""
    # Do not loop if no iterable provided.
    if not 'iterable' in params['var']:
        return params
    variable = getvariable(
        params['var']['iterable'],
        params['var']['delimiter'],
        params['var']['owner']
    )
    # Remove the rule from the tree.
    params['tree'] = {
        'closed': True,
        'contents': params['tree']['contents']
    }
    iterations = []
    for key, value in iterate(variable):
        # Set the key variable if provided.
        if 'key' in params['var']:
            setvariable(
                params['var']['key'],
                params['var']['delimiter'],
                key,
                params['var']['owner']
            )
        # Set the value variable if provided.
        if 'value' in params['var']:
            setvariable(
                params['var']['value'],
                params['var']['delimiter'],
                value,
                params['var']['owner']
            )
        # Walk for this iteration.
        iterations.append(walk(params)['string'])
    # Join the iterations.
    params['string'] = params['var']['join'].join(iterations)
    return params

def returning(params):
    """Prepare to return from this point on."""
    params['string'] = ''
    # If no more layers should be returned out of, don't.
    if not params['var']['layers']:
        return params
    # Decrement the amount of layers to return out of if a limit was defined.
    if not isinstance(params['var']['layers'], bool):
        params['var']['layers'] -= 1
    # Delete every node after this one.
    returningdelete(
        params['tree']['parent']['contents'],
        params['tree']['key'] + 1
    )
    # If this node was nested, attempt to return out of its parent.
    if params['var']['layers'] and 'parent' in params['tree']['parent']:
        params['tree']['parent'] = params['tree']['parent']['parent']
        params = returning(params)
    return params

def returningdelete(tree, limit = 0):
    """Delete contents of a tree to break references.
    
    ``tree``
        The contents of the tree.

    ``limit``
        What the length the tree contents should be limited to.

    Returns: void - Nothing. The contents of ``tree`` are modified.
    """
    while len(tree) > limit:
        # If this item is a dict.
        if isinstance(tree[limit], dict):
            returningdelete(tree[limit]['contents'])
        del tree[limit]

def savelocal(params):
    """Save the variables set before this section."""
    params['var']['local'] = {}
    for key, value in iterate(params['var']['owner']):
        params['var']['local'][key] = copy.deepcopy(value)
    return params

def setvariable(string, split, assignment, owner):
    """Set a variable based on a split string.

    ``string``
        str - The name of the variable to set.

    ``split``
        str - The string that separates the levels of the variable.

    ``assignment``
        mixed - The value to assign to the variable.

    ``owner``
        mixed - The object to set the variable on.

    Returns: void - Nothing. The variable is modified.
    """
    split = string.split(split)
    for key, value in enumerate(split):
        if key < len(split) - 1:
            try:
                owner = owner[value]
            except (AttributeError, TypeError):
                try:
                    owner = owner[int(value)]
                except (AttributeError, TypeError, ValueError):
                    owner = getattr(owner, value)
    try:
        owner[split[len(split) - 1]] = assignment
    except (AttributeError, TypeError):
        try:
            owner[int(split[len(split) - 1])] = assignment
        except (AttributeError, TypeError, ValueError):
            setattr(owner, split[len(split) - 1], assignment)

def templates(params):
    """Grab the unparsed contents of a template file."""
    # If the template is not whitelisted or blacklisted.
    if listing(params['string'], params['var']):
        params['string'] = open(
            os.path.normpath(params['string'])
        ).read()
    else:
        params['string'] = ''
    return params

def transform(params):
    """Send string as an argument for functions."""
    params['var']['string'] = params['string']
    return params

def trim(params):
    """Trim unnecessary whitespace."""
    trimrules = {
        '<pre':
        {
            'close': '</pre>',
            'skip': True
        },
        '<textarea':
        {
            'close': '</textarea>',
            'skip': True
        }
    }
    pos = suit.tokens(trimrules, params['string'], params['config'])
    tree = suit.parse(
        trimrules,
        pos,
        params['string'],
        params['config']
    )['contents']
    params['string'] = ''
    for value in tree:
        # If this node is a tag we do not want to trim the contents of, put
        # the statement back.
        if isinstance(value, dict):
            params['string'] += ''.join((
                value['rule'],
                value['contents'][0],
                trimrules[value['rule']]['close']
            ))
        # Else, trim it.
        else:
            params['string'] += ''.join((
                re.sub(
                    '(?m)[\s]+$',
                    '',
                    value
                ),
                value[
                    len(value.rstrip()):
                    len(value)
                ]
            ))
    # Remove the whitespace preceding the string.
    params['string'] = params['string'].lstrip()
    return params

def trying(params):
    """Try to walk and handle exceptions."""
    # If a variable is provided.
    if 'var' in params['var']:
        setvariable(
            params['var']['var'],
            params['var']['delimiter'],
            '',
            params['var']['owner']
        )
    # Try to walk through this node.
    try:
        params['string'] = suit.walk(
            params['rules'],
            params['tree'],
            params['config']
        )
    # Catch all exceptions.
    except Exception as e:
        # If a variable is provided.
        if 'var' in params['var']:
            setvariable(
                params['var']['var'],
                params['var']['delimiter'],
                e,
                params['var']['owner']
            )
        # Collapse the node.
        params['string'] = ''
    return params

def variables(params):
    """Grab a variable."""
    params['string'] = getvariable(
        params['string'],
        params['var']['delimiter'],
        params['var']['owner']
    )
    if params['var']['json']:
        params['string'] = json.dumps(
            params['string'],
            separators = (',', ':')
        )
    return params

def walk(params):
    """Walk through this node."""
    params['string'] = suit.walk(
        params['rules'],
        params['tree'],
        params['config']
    )
    return params

default = {
    'delimiter': '.',
    'equal': '=',
    'log': False,
    'owner': var,
    'quote': ('"', '\'')
}

rules = {
    '[':
    {
        'close': ']',
        'functions': [walk, bracket]
    },
    '[assign]':
    {
        'close': '[/assign]',
        'functions': [walk, attribute, decode, assign],
        'var':
        {
            'equal': default['equal'],
            'list': ('json', 'var'),
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'decode': ('json',),
                'delimiter': default['delimiter'],
                'json': 'false',
                'owner': default['owner']
            }
        }
    },
    '[assign':
    {
        'close': ']',
        'create': '[assign]',
        'skip': True
    },
    '[call':
    {
        'close': '/]',
        'functions': [walk, attribute, functions],
        'skip': True,
        'var':
        {
            'equal': default['equal'],
            'log': default['log'],
            'onesided': True,
            'quote': default['quote'],
            'var':
            {
                'delimiter': default['delimiter'],
                'function': '',
                'owner': None
            }
        }
    },
    '[comment]':
    {
        'close': '[/comment]',
        'skip': True
    },
    '[entities]':
    {
        'close': '[/entities]',
        'functions': [copyvar, walk, entities],
        'var':
        {
            'entities': True,
            'json': False
        }
    },
    '[execute]':
    {
        'close': '[/execute]',
        'functions': [walk, attribute, decode, execute],
        'var':
        {
            'equal': default['equal'],
            'list': ('log',),
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'decode': ('log',),
                'log': 'true'
            }
        }
    },
    '[execute':
    {
        'close': ']',
        'create': '[execute]',
        'skip': True
    },
    '[if]':
    {
        'close': '[/if]',
        'functions': [attribute, decode, condition],
        'var':
        {
            'equal': default['equal'],
            'list': ('condition', 'not'),
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'decode': ('not',),
                'delimiter': default['delimiter'],
                'not': 'false',
                'owner': default['owner']
            }
        }
    },
    '[if':
    {
        'close': ']',
        'create': '[if]',
        'skip': True
    },
    '[local]':
    {
        'close': '[/local]',
        'functions': [copyvar, savelocal, walk, loadlocal],
        'var':
        {
            'owner': default['owner']
        }
    },
    '[loop]':
    {
        'close': '[/loop]',
        'functions': [attribute, loop],
        'var':
        {
            'blacklist': True,
            'equal': default['equal'],
            'list': ('delimiter', 'owner'),
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'delimiter': default['delimiter'],
                'join': '',
                'owner': default['owner']
            }
        }
    },
    '[loop':
    {
        'close': ']',
        'create': '[loop]',
        'skip': True
    },
    '[return':
    {
        'close': '/]',
        'functions': [walk, attribute, decode, returning],
        'skip': True,
        'var':
        {
            'equal': default['equal'],
            'list': ('layers',),
            'log': default['log'],
            'onesided': True,
            'quote': default['quote'],
            'var':
            {
                'decode': ('layers',),
                'layers': 'true'
            }
        }
    },
    '[skip]':
    {
        'close': '[/skip]',
        'functions': [walk],
        'skip': True,
        'skipescape': True
    },
    '[template]':
    {
        'close': '[/template]',
        'functions': [copyvar, walk, templates],
        'var': {}
    },
    '[transform]':
    {
        'close': '[/transform]',
        'functions': [walk, attribute, transform, functions],
        'var':
        {
            'equal': default['equal'],
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'delimiter': default['delimiter'],
                'function': '',
                'owner': None,
                'string': ''
            }
        }
    },
    '[transform':
    {
        'close': ']',
        'create': '[transform]',
        'skip': True
    },
    '[trim]':
    {
        'close': '[/trim]',
        'functions': [walk, trim]
    },
    '[try]':
    {
        'close': '[/try]',
        'functions': [attribute, trying],
        'var':
        {
            'equal': default['equal'],
            'list': ('var',),
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'delimiter': default['delimiter'],
                'owner': default['owner']
            }
        }
    },
    '[try':
    {
        'close': ']',
        'create': '[try]',
        'skip': True
    },
    '[var]':
    {
        'close': '[/var]',
        'functions': [walk, attribute, decode, variables, entities],
        'var':
        {
            'equal': default['equal'],
            'list': ('entities', 'json'),
            'log': default['log'],
            'quote': default['quote'],
            'var':
            {
                'decode': ('entities', 'json'),
                'delimiter': default['delimiter'],
                'entities': 'true',
                'json': 'false',
                'owner': default['owner']
            }
        }
    },
    '[var':
    {
        'close': ']',
        'create': '[var]',
        'skip': True
    }
}