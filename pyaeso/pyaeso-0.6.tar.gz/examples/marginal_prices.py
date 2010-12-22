#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2010 Keegan Callin

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see
#~ <http://www.gnu.org/licenses/gpl-3.0.html>.

'''Print recent marginal pool prices and exit.'''

# Standard library imports
import sys
from StringIO import StringIO
from datetime import date
from datetime import timedelta

# 3rd Party Libraries
from pyaeso import ets

def  main():
    end_date = date.today() + timedelta(1)
    start_date = end_date - timedelta(2)

    f = StringIO()
    ets.dump_marginal_pool_price(f, start_date, end_date)
    f.seek(0)
    #print f.getvalue()

    print '''Recent Marginal Pool Prices:'''
    print 28*'='
    for t, price in ets.parse_marginal_pool_price_file(f):
        # Time calculations are easier when done in UTC so that no timezone
        # conversions or daylist-savings time conversions need to be made.  For
        # this reason all times yielded by pyaeso are UTC.
        #
        # UTC times are converted to local times when they are displayed to the
        # user.
        print t.astimezone(ets.ALBERTA_TZ), '$' + str(price)
    f.close()

    return(0)


if __name__ == '__main__':
    sys.exit(main())
