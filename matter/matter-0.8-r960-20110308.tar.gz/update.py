#!/usr/bin/env python

import os
#update docs and examples
os.system("""
cd docs
svn up
make html
login.cacr.caltech.edu:crystal
scp -r docs/_build/html/* jbrkeith@login.cacr.caltech.edu:projects/danse/docs.danse.us/docroot/inelastic/matter/sphinx
#scp -r useCases/mdDos/*.zip jbrkeith@login.cacr.caltech.edu:projects/danse/docs.danse.us/docroot/inelastic
""")
#update egg
os.system("""
cd src
python setup.py bdist_egg
scp dist/*.egg jbrkeith@login.cacr.caltech.edu:/cacr/home/proj/danse/packages/dev_danse_us
""")

