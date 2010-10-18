# Copyright (c) 2010 by Yaco Sistemas <lgs@yaco.es>
#
# This file is part of yaco.hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

version = "0.1.1"

from hghooks.trachooks import close, merge, noop


def verify(ticket):
    ticket['is_tested'] = '1'


def yaco_ticket_commands():
    return {
        'cierra': close,
        'corrige': close,
        'arregla': close,
        'ver': noop,
        'verify': verify,
        'verifica': verify,
        }


def yaco_token_commands():
    return {
        'mezclado en': merge,
        'mezclamos en': merge,
        }
