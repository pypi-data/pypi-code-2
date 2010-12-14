# Copyright (C) 2002-2006 gocept gmbh & co.kg, 06112 Halle(Saale), Germany
# Christian Zagrodnick, cz@gocept.com
# Michael Howitz, mh@gocept.com
# $Id: RenderPostgres.py 31512 2010-12-14 10:13:34Z mac $
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from RenderDB import Render as RenderBase

class Render(RenderBase):
    """Postgres renderer."""

    _abstract = False

    def renderTableFooter(self):
        return " WITHOUT OIDS;\n"


            
