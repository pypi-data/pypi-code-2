# -*- coding: utf-8 -*-

from datetime import date

"""
This is the FridayThe13th module and it provides one function called phobia(upToYear)
which prints the nearest fridays the 13th up to the year upToYear in order to make you careful.
"""

def phobia(upToYear):
    """
    This is the function called phobia(upToYear) which prints the nearest
    fridays the 13th up to the year upToYear in order to make you careful.
    """
    isoFriday = 5
    monthsInYear = 12
    print("Dates to remember: ")
    for y in range(date.today().year, upToYear):
        for m in range(1, monthsInYear + 1):
            if date(y, m, 13).isoweekday() == isoFriday:
                print(date(y, m, 13))

