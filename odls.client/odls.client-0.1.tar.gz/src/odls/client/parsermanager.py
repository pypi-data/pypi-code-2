"""A manager for parsing modules.
"""
##
## parsermanager.py
## Login : <uli@pu.smp.net>
## Started on  Tue Apr 20 17:13:15 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

class ODLSParserManager(object):

    def __init__(self, app):
        self.app = app
        self.logger = self.app.logger
        self.logger.debug('Initializing module manager for file parsers')

    def stop(self):
        self.logger.debug('Shutting down module manager')
        self.logger.debug('Done.')
