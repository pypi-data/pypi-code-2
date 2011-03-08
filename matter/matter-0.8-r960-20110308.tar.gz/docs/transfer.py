#!/usr/bin/env python

su jbk
svn up
make html
scp -r _build/html/ jbrkeith@login.cacr.caltech.edu:crystal
