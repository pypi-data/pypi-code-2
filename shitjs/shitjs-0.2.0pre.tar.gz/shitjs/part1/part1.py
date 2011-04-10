"""

Tokenise simple expressions like "1 + 2 * 4".

Produce an array of simple token objects from a string.

A simple token object contains these members:
    type: 'name', 'string', 'number', 'operator'
    value: string or number value of the token
    from: index of first character of the token
    to: index of the last character + 1

For example:
    {"type":"name",
    "value":"i_can_has_cheezbrgr",
    "from":9,
    "to":28}


Let's use pretty print (pprint) to make the results more readable.
    >>> from pprint import pprint

    >>> pprint(list(tokenise("1")))
    [{'from': 0, 'to': 1, 'type': 'number', 'value': 1.0}]


    >>> pprint(list(tokenise("1 + 4")))
    [{'from': 0, 'to': 1, 'type': 'number', 'value': 1.0},
     {'from': 2, 'to': 3, 'type': 'operator', 'value': '+'},
     {'from': 4, 'to': 5, 'type': 'number', 'value': 4.0}]

    >>> pprint(list(tokenise("1 + 2 * 4")))
    [{'from': 0, 'to': 1, 'type': 'number', 'value': 1.0},
     {'from': 2, 'to': 3, 'type': 'operator', 'value': '+'},
     {'from': 4, 'to': 5, 'type': 'number', 'value': 2.0},
     {'from': 6, 'to': 7, 'type': 'operator', 'value': '*'},
     {'from': 8, 'to': 9, 'type': 'number', 'value': 4.0}]

Now for some error checking!
    >>> pprint(list(tokenise("1 + a4")))
    Traceback (most recent call last):
    ...
    ParseError: ('a4', 4)

"""

operators = ['/', '+', '*', '-']
class ParseError(Exception):
    pass
def is_operator(s):
    return s in operators
def is_number(s):
    return s.isdigit()

def tokenise(expression):
    pos = 0
    for s in expression.split():
        t = {}
        if is_operator(s):
            t['type'] = 'operator'
            t['value'] = s
        elif is_number(s):
            t['type'] = 'number'
            t['value'] = float(s)
        else:
            raise ParseError(s, pos)
 
        t.update({'from': pos, 'to': pos + len(s)})
        pos += len(s) + 1
        yield t
 


if __name__ == "__main__":
    import doctest
    doctest.testmod()



