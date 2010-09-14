#! /usr/bin/env python
'''
Created on Aug 18, 2010

@author: dwmclary
'''
import sys
def read_map_output(file):
    for line in file:
        yield line
def main():
    data = read_map_output(sys.stdin)
    for line in data:
        print line.strip()


if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except:
        pass
    main()