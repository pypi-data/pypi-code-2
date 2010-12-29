##    shitjs - a shit javascript interpreter
##    Copyright (C) 2009, 2010, 2011 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com


import unittest

try:
    import part1
except:
    from shitjs import part1

class TestPart1(unittest.TestCase):
    def test_tokenise(self):
        self.assertEqual(list(part1.tokenise("1 + 2 * 4")), 
                         [{'from': 0, 'to': 1, 'type': 'number', 'value': 1.0},
                          {'from': 2, 'to': 3, 'type': 'operator', 'value': '+'},
                          {'from': 4, 'to': 5, 'type': 'number', 'value': 2.0},
                          {'from': 6, 'to': 7, 'type': 'operator', 'value': '*'},
                          {'from': 8, 'to': 9, 'type': 'number', 'value': 4.0}] )

if __name__ == '__main__':
    unittest.main()

