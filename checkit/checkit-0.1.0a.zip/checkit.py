"""Checkit is a tool to validate executable specifications
created with BDD style grammar.

The checkit module is simply a wrapper around nose to discover
and execute specifications using flexible matching rules.
"""
import os
import sys


def main():
    """A simple wrapper that calls nosetests
    with a regex of keywords to use in discovering specs
    """
    return os.system('nosetests \
        --with-doctest \
        -i "^(Describe|it|should)" \
        -i "(Spec[s]?)$" \
        -i "(specs?|examples?)(.py)?$" ' + ' '.join(sys.argv[1:]))


if __name__ == '__main__':
    main()
