# -*- coding: utf-8 -*-
#
# File: UIDRenamer.py
#
# Copyright (c) 2007 by Associação Python Brasil
# Generator: ArchGenXML 
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Jean Rodrigo Ferri / Dorneles Treméa / Fabiano Weimar / Rodrigo Senra /
Érico Andrei <contato@pythobrasil.com.br>"""
__docformat__ = 'plaintext'

##code-section module-header #fill in your manual code here
##/code-section module-header



class UIDRenamer:
    """
    """

    ##code-section class-header_UIDRenamer #fill in your manual code here
    ##/code-section class-header_UIDRenamer

    def generateNewId(self):
        """Suggest an id for this object.
        This id is used when automatically renaming an object after creation.
        """
        return self.UID()


##code-section module-footer #fill in your manual code here
##/code-section module-footer


