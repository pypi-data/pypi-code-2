#!/usr/bin/env python

import array

def gen_dot_letter_dict(path):
    with open(path, 'U') as f:
        data = [x.split('\n', 1) for x in f.read().strip().split('\n\n')]
        data_dict = {}
        for char, dat in data:
            dat = tuple(tuple(int(y) for y in x.replace(' ', '0')) for x in dat.split('\n'))
            dat_max = max(map(len, dat))
            data_dict[char] = (dat_max, dat)
    return data_dict

def gen_dot_letter_python_code(path):
    return str(gen_dot_letter_dict(path)).replace(', ', ',').replace(': ', ':')

if __name__ == '__main__':
    import sys
    try:
        sys.stdout.write('%s\n' % gen_dot_letter_python_code(sys.argv[1]))
    except IndexError:
        sys.stderr.write('no file given!\n')
