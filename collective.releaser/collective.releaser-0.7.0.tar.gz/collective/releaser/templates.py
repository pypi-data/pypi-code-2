# -*- coding: utf-8 -*-
## Copyright (C)2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
""" Template definitions
"""
from paste.script import templates
from zopeskel.base import var

class ReleaserProject(templates.Template):
    """ Generates a Buildout project tree 
    """
    _template_dir = 'templates/releaser_project'
    summary = 'A Buildout project tree'
    use_cheetah = True

    vars = [var('project_name', 'Project Name'),
            var('project_repo', 'Project Subversion root')]


