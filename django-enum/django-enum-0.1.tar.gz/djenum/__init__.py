import re
import itertools


class ChoiceEnum(object):
    """
    A class to simplify the creation of Django choice enumerations.

    To generate an integer enum, starting at 1, it suffices to give a
    list of strings, or even a single string that will be split on
    whitespace:

    >>> color_choices = ChoiceEnum('red green blue yellow brown')
    >>> color_choices.RED
    1
    >>> color_choices.GREEN
    2

    The enum tuples can be accessed by index as well (as Django
    requires):

    >>> color_choices[3]
    (4, 'yellow')

    You can also pass in a list of value / name tuples, with value of
    any type:

    >>> cc_types = ChoiceEnum((('AMEX', 'American Express'), ('VISA', 'Visa')))
    >>> cc_types.AMERICAN_EXPRESS
    'AMEX'

    To facilitate making string enumerations where the value and name
    are identical, you can set the constructor parameter 'enum_is_int'
    to a false value, and avoid having to specify tuples:

    >>> cc_types = ChoiceEnum('AMEX VISA DISCOVER', 0)
    >>> cc_types.DISCOVER
    'DISCOVER'

    Or, equivalently, use StringChoiceEnum, which does this for you.

    """

    def __init__(self, choices, enum_is_int=True):

        self._enum_is_int = enum_is_int
        if isinstance(choices, basestring):
            choices = choices.split()
        if isinstance(choices, (list, tuple)) and \
               all(isinstance(x, tuple) and len(x) == 2 for x in choices):
            values = choices
        else:
            if enum_is_int:
                values = zip(itertools.count(1), choices)
            else:
                values = [(x, x) for x in choices]

        for v, n in values:
            # some useful cleanup
            attr = n.upper().replace(' ', '_').replace('-', '_').replace('_&_', '_AND_')
            attr = re.sub('[^A-Za-z0-9_-]', '', attr)
            setattr(self, attr, v)
        self._choices = values

    def __getitem__(self, idx):
        return self._choices[idx]

    def get_name_for_value(self, value):
        for v, n in self._choices:
            if v == value:
                return n


class StringChoiceEnum(ChoiceEnum):
    """
    Like a ChoiceEnum, but with string values by default.

    >>> color_choices = StringChoiceEnum('red green blue yellow brown')
    >>> color_choices.RED
    'red'
    >>> color_choices.GREEN
    'green'
    
    """
    def __init__(self, choices):
        super(StringChoiceEnum, self).__init__(choices, enum_is_int=False)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
