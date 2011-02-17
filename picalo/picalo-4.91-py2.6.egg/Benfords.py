#!/usr/bin/python

####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
#                                                                                  #
# This file is part of Picalo.                                                     #
#                                                                                  #
# Picalo is free software; you can redistribute it and/or modify                   #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# Picalo is distributed in the hope that it will be useful,                        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################
#
# Version 1.00
# Jun 22, 2005: Added summary_analyze.
#               Made the analyze function ignore numbers that don't have enough digits
# Dec 10, 2003: Version 1.00.  Tested using unittest.  
# Dec 08, 2003: Started this log.
#
#
#
####################################################################################

__doc__ = '''
The Benfords module performs digital analyses on data sets.  In the 1930's, Benford
realized that many number sets (now known to include invoice amounts and stock prices)
followed a certain pattern.  A 1 appeared as the first digit about 30 percent of the time.
Each digit in the number has a probability associated with which number it might be.

Numbers that are created by people (who obviously don't know about Benford's Law)
do not follow Benford's distribution.  In recent years, Benford's Law has been used
to separate values that occur naturally in business and those that are fabricated.
'''

  
    

# a listing of the public functions in this module (used by Manual.py)
__functions__ = (
  'analyze',
  'calc_benford',
  'get_expected',
)



import math, types
from lib import stats
import Grouping, Simple
from picalo import Table, TableArray, check_valid_table
from picalo.base.Global import run_tablearray
from picalo.base.Number import number


def calc_benford(position, digit, base=10):
  '''Helper function that codes benford's actual formula
     The generalized formula was found at http://www.mathpages.com/home/kmath302/kmath302.htm
     This method calculates the probability at a given digit is in a given position.
     
     @param position:  The position in the number (0=first digit, 1=second digit, ...)
     @type  position:  int
     @param digit:     The actual number (0,1,2,3,4,5,6,7,8,9) this digit is
     @type  digit:     int
     @param base:      The number base.  Optional (default is 10)
     @type  base:      int
     @return:          The Benford probability (the percentage of the time this position will have this digit).
     @rtype:           float
  '''
  assert isinstance(position, (types.IntType, types.LongType, types.FloatType)), 'Invalid position: ' + str(position)
  assert isinstance(digit, (types.IntType)), 'Invalid digit: ' + str(digit)
  assert isinstance(base, (types.IntType)), 'Invalid base: ' + str(base)
  part1 = 1 / math.log(base)
  if position == 0: k = 0
  else: k = math.pow(base, position - 1)  # bottom of the summation
  k_stop = math.pow(base, position) - 1 # top of the summation
  part2 = 0.0
  while k <= k_stop:
    part2 += math.log(1.0 + (1.0 / (k * base + digit)))
    k += 1
  return part1 * part2
  

def get_expected(number, number_of_significant_digits=1):
  '''Calculates Benford's expected probability for a given number to a certain number of digits.
     For example, given the number 1234, calulate the combined probability that a 1 appears
     as the first digit, a 2 appears as the second digit, and so forth, to the number of desired
     significant digits.
     
     @param number:                       The number (1234 in the example) to calculate the probability for
     @type  number:                       float
     @param number_of_significant_digits: The number of positions to use for the probability.  In the example, a value of 2 means to calculate the probability for the number 12.
     @type  number_of_significant_digits: int
     @return:                             The expected frequency of this number according to Benford's Law.
     @rtype:                              float
  '''
  assert isinstance(number, (types.IntType, types.LongType, types.FloatType, types.StringType, types.UnicodeType)), 'Invalid number: ' + str(number)
  assert isinstance(number_of_significant_digits, types.IntType), 'Invalid number of significant digits: ' + str(number_of_significant_digits)
  probability = 1.0
  numst = str(number)
  assert len(numst) >= number_of_significant_digits, str(len(numst)) + ' is not long enough to calculate a Benford probability at ' + str(number_of_significant_digits) + ' digits.'
  for pos in range(0, number_of_significant_digits):
    probability *= calc_benford(pos, int(numst[pos]))  # multiply since it is a statistical AND
  return probability


    
class Result:
  '''A simple class to represent a result statistic for an individual data point'''
  def __init__(self, number, significant_digits):
    self.number = number
    self.significant_digits = significant_digits
    self.frequency = 0
    self.expected = 0
    
  def __repr__(self):
    return 'Result (num, sign, freq, exp, diff): ' + '\t'.join([ str(self.number), self.significant_digits, str(self.frequency), str(self.expected), str(math.fabs(self.frequency - self.expected)) ])



def analyze(table, col, number_of_significant_digits=1):
  '''Performs a Benford's analysis on a table column.  Returns a picalo table.
     The frequency and expected values will be 0 for items that were not analyzed 
     (due to insufficient digits).
     
     Important: if you ask for 2 significant digits, any input numbers that
     do not have two digits are ignored and not included in the results.  If these 
     numbers were not ignored, the analysis would throw errors.
     
     Example:
     
      >>> table = Table([('col000', unicode), ('col001', int), ('col002', int)], [
      ...             ['Dan',10,8],
      ...             ['Sally',12,12],
      ...             ['Dan',11,15], 
      ...             ['Sally',12,14], 
      ...             ['Dan',11,16], 
      ...             ['Sally',15,15], 
      ...             ['Dan',16,15], 
      ...             ['Sally',13,14]])
      >>> results = Benfords.analyze(table, 1, number_of_significant_digits=2)            
      >>> results.view()
      +--------+--------------------+------------------+----------------------+-----------------+
      | Number | Significant Digits | Actual Frequency | Expected Probability |    Difference   |
      +--------+--------------------+------------------+----------------------+-----------------+
      |     10 | 10                 |            0.125 |      0.0360270497068 | 0.0889729502932 |
      |     12 | 12                 |             0.25 |      0.0327585353738 |  0.217241464626 |
      |     11 | 11                 |             0.25 |      0.0342843373349 |  0.215715662665 |
      |     12 | 12                 |             0.25 |      0.0327585353738 |  0.217241464626 |
      |     11 | 11                 |             0.25 |      0.0342843373349 |  0.215715662665 |
      |     15 | 15                 |            0.125 |      0.0291027478744 | 0.0958972521256 |
      |     16 | 16                 |            0.125 |      0.0281085963079 | 0.0968914036921 |
      |     13 | 13                 |            0.125 |       0.031406327064 |  0.093593672936 |
      +--------+--------------------+------------------+----------------------+-----------------+     
     
     Example 2:
     I usually add a column for the difference from Benford's expectation to the table, 
     then summarize to get an average difference per vendor, employee, etc.
     Individual numbers will often not match Benford, but averages across several 
     numbers should match.

      >>> table = Table([('col000', unicode), ('col001', int), ('col002', int)], [
      ...             ['Dan',10,8],
      ...             ['Sally',12,12],
      ...             ['Dan',11,15], 
      ...             ['Sally',12,14], 
      ...             ['Dan',11,16], 
      ...             ['Sally',15,15], 
      ...             ['Dan',16,15], 
      ...             ['Sally',13,14]])
      >>> table.append_column('ben_diff', Benfords.analyze(table, 1, 2).column(4))
      >>> table.view()
      +--------+--------+--------+-----------------+
      | col000 | col001 | col002 |     ben_diff    |
      +--------+--------+--------+-----------------+
      | Dan    |     10 |      8 | 0.0889729502932 |
      | Sally  |     12 |     12 |  0.217241464626 |
      | Dan    |     11 |     15 |  0.215715662665 |
      | Sally  |     12 |     14 |  0.217241464626 |
      | Dan    |     11 |     16 |  0.215715662665 |
      | Sally  |     15 |     15 | 0.0958972521256 |
      | Dan    |     16 |     15 | 0.0968914036921 |
      | Sally  |     13 |     14 |  0.093593672936 |
      +--------+--------+--------+-----------------+
      >>> results = Grouping.summarize_by_value(table, 'col000', 
      ...           ben_avg="sum(group['ben_diff']) / len(group)")
      >>> results.view()
      +----------+--------+----------------+
      | StartKey | EndKey |    ben_avg     |
      +----------+--------+----------------+
      | Dan      | Dan    | 0.154323919829 |
      | Sally    | Sally  | 0.155993463579 |
      +----------+--------+----------------+

     @param table:                         A Picalo table
     @type  table:                         Table
     @param col:                           The column to be analyzed.
     @type  col:                           str
     @param number_of_significant_digits:  The number of leading digits to use in the analysis.  Higher numbers (3-5) require more data for statistical power.
     @type  number_of_significant_digits:  int
     @return:                              A Picalo table describing the results of the analysis.
     @rtype:                               Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating digital analysis...', analyze, table, col, number_of_significant_digits=number_of_significant_digits)
  check_valid_table(table, col)
  assert isinstance(number_of_significant_digits, types.IntType), 'Invalid number of significant digits: ' + str(number_of_significant_digits)
  list_of_numbers = table.column(col)
  # calculate the distribution of the digits
  digits = {}
  stats = Table([ ('Number', int), ('SignificantDigits', int), ('ActualFrequency', float), ('ExpectedProbability', float)])
  stats.append_calculated('Difference', number, "abs(record['ActualFrequency'] - record['ExpectedProbability'])")
  for num in list_of_numbers:
    numst = str(num)[0: number_of_significant_digits]
    if len(numst) != number_of_significant_digits:  # ignore any numbers that don't have enough digits
      continue
    stats.append([num, numst, 0, 0])
    if len(numst) == number_of_significant_digits:
      if digits.has_key(numst): 
        count = digits[numst] + 1
      else: 
        count = 1
      digits[numst] = count  
  # add the frequency and expected to the stats
  total_count = float(len(list_of_numbers))
  for stat in stats:
    count = digits[str(stat['SignificantDigits'])]
    stat['ActualFrequency'] = count / total_count
    try:
      stat['ExpectedProbability'] = get_expected(stat['SignificantDigits'], number_of_significant_digits) 
    except:
      stat['ActualFrequency'] = 0
      stat['ExpectedProbability'] = 0
    
  # return the statistics
  return stats



