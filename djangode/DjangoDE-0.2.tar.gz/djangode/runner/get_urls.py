# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from django.core.urlresolvers import get_resolver, RegexURLResolver, RegexURLPattern

def get_urls():
    resolver = get_resolver(None)

    return [process_urls(pattern) for pattern in resolver.url_patterns]

def process_urls(pattern):
    if isinstance(pattern, RegexURLResolver):
        return (pattern.regex.pattern, [process_urls(subpattern) for subpattern in pattern.url_patterns])
    elif isinstance(pattern, RegexURLPattern):
        return (pattern.regex.pattern, (pattern.callback.func_code.co_filename, pattern.callback.func_code.co_firstlineno), pattern.name)
    else:
        print pattern
