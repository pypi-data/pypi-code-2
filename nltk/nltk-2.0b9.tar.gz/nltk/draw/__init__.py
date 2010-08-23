# Natural Language Toolkit: graphical representations package
#
# Copyright (C) 2001-2010 NLTK Project
# Author: Edward Loper <edloper@gradient.cis.upenn.edu>
#         Steven Bird <sb@csse.unimelb.edu.au>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT
#
# $Id: __init__.py 8479 2010-01-13 05:40:34Z StevenBird1 $

# Import Tkinter-based modules if Tkinter is installed
try:
    import Tkinter
except ImportError:
    import warnings
    warnings.warn("nltk.draw package not loaded "
                  "(please install Tkinter library).")
else:
    from cfg import *
    from tree import *
    from dispersion import dispersion_plot

    # Make sure that nltk.draw.cfg and nltk.draw.tree refer to the correct
    # modules (and not to nltk.cfg & nltk.tree)
    import cfg, tree

