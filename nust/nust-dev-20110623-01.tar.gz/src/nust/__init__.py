#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function 

__name__ = 'nust'
__all__ = ['body']

import sys
from nust.body import *

#---------------------------------------------------------------
#---------------------------------------------------------------
def main():
    parse_args()
    sys.exit(main_process())

if __name__ == "__main__":
    main()
