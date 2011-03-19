# koboldfs
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

VERSION             = '0.3'
BLOCKSIZE           = 1024*1024

RES_REDIRECT        = '\x00'
RES_OK              = '\x01'
RES_WAITING         = '\x02'
RES_TRANSFER        = '\x03'
RES_KO              = '\x04'
RES_ERR_DOMAIN      = '\x05'
RES_ERR_COMMAND     = '\x06'
RES_ERR_NOTFOUND    = '\x07'
RES_ERR_RESET       = '\x08'

CMD_PING            = '\x10'
CMD_PUT             = '\x11'
CMD_GET             = '\x12'
CMD_GET_URL         = '\x13'
CMD_DELETE          = '\x14'

CMD_PREPARE         = '\x20'
CMD_COMMIT          = '\x21'
CMD_ABORT           = '\x22'
