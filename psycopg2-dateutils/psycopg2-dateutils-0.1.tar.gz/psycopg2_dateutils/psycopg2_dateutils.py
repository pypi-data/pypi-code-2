#!/usr/bin/env python

import psycopg2.extensions
import dateutils

def parse_interval(value, cur):
    last_number = None
    years = 0
    months = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    microseconds = 0

    for token in value.split():
        try:
            last_number = int(token)
        except ValueError:
            if token.startswith('y'):
                years += last_number
                last_number = None
            elif token.startswith('m'):
                months += last_number
                last_number = None
            elif token.startswith('w'):
                days += last_number * 7
                last_number = None
            elif token.startswith('d'):
                days += last_number
                last_number = None
            elif ':' in token:
                h, m, s = token.split(':')
                hours = int(h)

                sign = cmp(hours, 0)

                minutes = int(m) * sign
                seconds, microseconds = (int(v)*sign for v in divmod(float(s), 1))

    delta = dateutils.relativedelta(
        years=years, months=months, days=days,
        hours=hours, minutes=minutes, seconds=seconds,
        microseconds=microseconds)  

    return delta

def tokenize_array(value):
    STATE_START_ELT=0
    STATE_NORMAL=1
    STATE_QUOTED=2
    STATE_ESCAPE=3
    STATE_END_ELT=4

    state = STATE_START_ELT
    token = []

    for i, c in enumerate(value):
        if state == STATE_START_ELT:
            if c == '"':
                state = STATE_QUOTED
            else:
                token.append(c)
                state = STATE_NORMAL
        elif state == STATE_NORMAL:
            if c == ',':
                yield ''.join(token)
                token = []
                state = STATE_START_ELT
            elif c in ('\\', '"'):
                raise ValueError('Malformed array literal {0}, unexpected {1} in position {2}'.format(value, c, i))
            else:
                token.append(c)
        elif state == STATE_QUOTED:
            if c == '\\':
                state = STATE_ESCAPE
            elif c == '"':
                state = STATE_END_ELT
            else:
                token.append(c)
        elif state == STATE_ESCAPE:
            token.append(c)
            state = STATE_QUOTED
        elif state == STATE_END_ELT:
            if c == ',':
                yield ''.join(token)
                token = []
                state = STATE_START_ELT
            else:
                raise ValueError('Malformed array literal {0}, unexpected {1} in position {2}'.format(value, c, i))

    if token:
        yield ''.join(token)


def parse_array(value, cur, element_parser):
    if not (value.startswith('{') and value.endswith('}')):
        raise ValueError('Invalid array literal')

    value = value[1:-1]

    return [element_parser(t, cur) for t in tokenize_array(value)]

def parse_interval_array(value, cur):
    return parse_array(value, cur, parse_interval)


def register():
    INTERVAL_oids = psycopg2.extensions.INTERVAL.values
    INTERVALARRAY_oids = psycopg2.extensions.INTERVALARRAY.values

    INTERVAL = psycopg2.extensions.new_type(INTERVAL_oids, 'INTERVAL', parse_interval)
    psycopg2.extensions.register_type(INTERVAL)

    INTERVALARRAY = psycopg2.extensions.new_type(INTERVALARRAY_oids, 'INTERVALARRAY', parse_interval_array)
    psycopg2.extensions.register_type(INTERVALARRAY)

register()
