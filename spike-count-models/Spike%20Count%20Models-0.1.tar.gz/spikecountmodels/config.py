# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2010 Bernstein Center for Computational Neuroscience Berlin   #
# author: André Großardt, based on Matlab code from Arno Onken                #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################
#
# === ChangeLog ============================================================= #
# 2010-09-15: First release version
# =========================================================================== #
#
###############################################################################

"""
Python Spikecount Models, configuration file
"""

DATA_DIR            = 'data'
"""Directory where output data files are stored"""
TMP_DATA_DIR        = 'data/tmp'
"""Directory for temporary data"""
DATA_FILE_SUFFIX    = '.dat'
"""Suffix for data files"""
MC_TMPFILE_PREFIX   = 'mctmp_'
"""File prefix for temporary datafiles of Monte-Carlo sampling"""
WHILE_LOOP_ABORT    = 1000000
"""Critical while loops will be aborted with an OverflowException after this
number of runs to avoid endless loops
"""

DEBUG               = False
"""If this is set to True, more information will be printed to the standard
output
"""
