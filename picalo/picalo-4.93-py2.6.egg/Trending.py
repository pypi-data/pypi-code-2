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
# Version 0.02
# Nov 15, 2004: Added routines from Aaron Bartholemew
# Sep 08, 2004: Added the cusum function.
# Dec 08, 2003: Version 0.01.  Started this log.
#
####################################################################################

from __future__ import division

__doc__ = '''
The Trending module contains functions that highlight trends in data.  Since fraud
is most often found in changes over time, this module is useful in looking at trends
over time.
'''

__functions__ = (
  'cusum',  
  'highlow_slope',
  'average_slope',
  'regression',
  'handshake_slope',
)

from math import sqrt
import re, types
from picalo import Table, TableArray, check_valid_table, run_tablearray, ensure_unique_colname


def cusum(table, col):
  '''Calculates a cusum, a cumulative difference in the values of a list
     at each row in the table.
     The cusum calculation gives a sense of the overall direction of a
     curve.
  
     Example:
     >>> table = Table([('col000', int), ('col001', int)], ([5,6], [3,2], [4,6]))
     >>> cusum = Trending.cusum(table, 0)  # cusum the first column (5, 3, 4)
     >>> cusum.view()
     +--------------+
     | col000_cusum |
     +--------------+
     |            0 |
     |           -2 |
     |           -1 |
     +--------------+

     @param table:  The table to be cusumed.
     @type  table:  Table or TableArray
     @param col:    The column name or index to cusum.
     @type  col:    str
     @return:       A new table containing a single column for the cusum value.
     @rtype:        Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating...', cusum, table, col)
  check_valid_table(table, col)
  cusumcol = ensure_unique_colname(table, table.column(col).name + '_cusum')
  results = Table([(cusumcol, table.column(col).column_type)])
  results.append([0])
  for i in range(1, len(table)):
    results.append([table[i][col] - table[i-1][col] + results[-1][0]])
  return results
  
 

def highlow_slope(table, ycol, xcol=None):
  '''Computes a slope based on the minimum Y and the X that goes with it and the maximum Y and the X that goes with it. 
     Returns the X that goes with the minimum Y, the minimum Y, the X that goes with the maximum Y, the maximum Y, and the slope.
     
     If xcol is None, it is generated starting as 0, 1, 2, 3, etc.
 
     Example:
      >>> table = Table([('col000', unicode), ('col001', int), ('col002', int)], [
                     ['Dan',10,8],
                     ['Sally',12,12],
                     ['Dan',11,15], 
                     ['Sally',12,14], 
                     ['Dan',11,16], 
                     ['Sally',15,15], 
                     ['Dan',16,15], 
                     ['Sally',13,14]])
      >>> results = Trending.highlow_slope(table, 2, 1)
      >>> results.view()
      +------+------+------+------+-------+
      | MinX | MinY | MaxX | MaxY | Slope |
      +------+------+------+------+-------+
      |   10 |    8 |   11 |   16 |   8.0 |
      +------+------+------+------+-------+

     @param table: The table to calculate the slope on
     @type  table: Table
     @param ycol:  The y column to use.  The maximum and minimum are taken from this column.
     @type  ycol:  str
     @param xcol:  The x column to use.  This is optional.
     @type  xcol:  str
     @return:      A table with the first record giving the x and y of the minimum y, the x and y of the maximum y, and the slope betwee the two points.
     @rtype:       Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating...', highlow_slope, table, ycol, xcol)
  check_valid_table(table, ycol)
  if xcol != None:
    check_valid_table(table, xcol)
  YPoints = table.column(ycol)
  ytype = table.column(ycol).column_type
  if xcol != None:
    XPoints = table.column(xcol)
    xtype = table.column(xcol).column_type
  else:
    XPoints = range(len(table))
    xtype = int
  MaxX=0
  MaxY=0
  MinX=0
  MinY=0
  count=0
  for Point in XPoints:
    Y=YPoints[count]
    X=Point
    if(count==0):
      MaxX=X
      MinX=X
      MaxY=Y
      MinY=Y
    if(MaxY<Y): 
      MaxX=X
      MaxY=Y
    if(MinY>Y): 
      MinX=X
      MinY=Y
    count=count+1
  ret = Table([('MinX', xtype), ('MinY', ytype), ('MaxX', xtype), ('MaxY', ytype), ('Slope', float)])
  r = ret.append()
  r['MinX'] = MinX
  r['MinY'] = MinY
  r['MaxX'] = MaxX
  r['MaxY'] = MaxY
  r['Slope'] = slope(MinX, MinY, MaxX, MaxY)
  return ret


def average_slope(table, ycol, xcol=None):
  '''Computes the average of the slopes between the points given.
     If xcol is None, it is generated starting as 0, 1, 2, 3, etc.

     Example:
      >>> from picalo import *
      >>> table = Table([('col000', unicode), ('col001', int), ('col002', int)], [
                     ['Dan',10,8],
                     ['Sally',12,12],
                     ['Dan',11,15], 
                     ['Sally',12,14], 
                     ['Dan',11,16], 
                     ['Sally',15,15], 
                     ['Dan',16,15], 
                     ['Sally',13,14]])
      >>> results = Trending.average_slope(table, 2, 1)
      >>> results.view()
      +-----------------+
      |  Average Slope  |
      +-----------------+
      | -0.559523809524 |
      +-----------------+

     @param table:  The table to calculate the slope on
     @type  table:  Table
     @param ycol:   The y column to use.  The maximum and minimum are taken from this column.
     @type  ycol:   str
     @param xcol:   The x column to use.  This is optional.
     @type  xcol:   str
     @return:       The average slope between points
     @rtype:        Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating...', average_slope, table, ycol, xcol)
  check_valid_table(table, ycol)
  if xcol != None:
    check_valid_table(table, xcol)
  YPoints = table.column(ycol)
  if xcol != None:
    XPoints = table.column(xcol)
  else:
    XPoints = range(len(table))
  length = len(XPoints)-1  #zero based
  counter=0
  Sum = 0
  Total=[]
  while(counter<length):
    Total.append(slope(XPoints[counter], YPoints[counter], XPoints[counter+1], YPoints[counter+1]))
    counter=counter+1
  for set in Total:
    Sum=Sum+set
  return Table([('Average_Slope', float)], [[Sum/length]])


def slope(X1, Y1, X2, Y2):
  '''
     Calculated the slope between the two points given.
  '''
  assert isinstance(X1, (types.IntType, types.LongType, types.FloatType)), 'Invalid number: ' + X1
  assert isinstance(X2, (types.IntType, types.LongType, types.FloatType)), 'Invalid number: ' + X2
  assert isinstance(Y1, (types.IntType, types.LongType, types.FloatType)), 'Invalid number: ' + Y1
  assert isinstance(Y2, (types.IntType, types.LongType, types.FloatType)), 'Invalid number: ' + Y2
  return ((Y2-Y1)/(X2-X1))


def regression(table, ycol, xcol=None):
  '''Computes the regressionline for the points given.
     Returns the slope, intercept, correlation, and r-squared value of the regression line for the Points
     If xcol is None, it is generated starting as 0, 1, 2, 3, etc.

     Example:
      >>> from picalo import *
      >>> table = Table([('col000', unicode), ('col001', int), ('col002', int)], [
                     ['Dan',10,8],
                     ['Sally',12,12],
                     ['Dan',11,15], 
                     ['Sally',12,14], 
                     ['Dan',11,16], 
                     ['Sally',15,15], 
                     ['Dan',16,15], 
                     ['Sally',13,14]])
      >>> results = Trending.regression(table, 1)
      >>> results.view()
      +----------------+---------------+-----------------+------------------+
      |     Slope      |   Intercept   |   Correlation   |     RSquared     |
      +----------------+---------------+-----------------+------------------+
      | 0.619047619048 | 10.3333333333 | 0.0428888771398 | 0.00183945578231 |
      +----------------+---------------+-----------------+------------------+

     @param table:  The table to calculate the simple regression on
     @type  table:  Table
     @param ycol:   The y column to use  
     @type  ycol:   str
     @param xcol:   The x column to use.  This is optional.
     @type  xcol:   str
     @return:       A table containing the slope, intercept, correlation, and rSquared
     @rtype:        Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating...', regression, table, ycol, xcol)
  check_valid_table(table, ycol)
  if xcol != None:
    check_valid_table(table, xcol)
  YPoints = table.column(ycol)
  if xcol != None:
    XPoints = table.column(xcol)
  else:
    XPoints = range(len(table))
  Ysum=0
  Xsum=0
  XSq=0
  XY=0
  slope=0
  length=len(XPoints)
  counter=0
  Returns=[]
  for Point in XPoints:
    X=Point
    Y=YPoints[counter]
    Ysum=Ysum+Y
    Xsum=Xsum+X
    XSq=XSq + X*X
    XY=XY+X*Y
    counter=counter+1
  rise=(length*XY)-(Xsum*Ysum)
  run=(length*XSq)-(Xsum*Xsum)
  slope=float(rise)/float(run)
  intercept = (Ysum - (slope*Xsum))/length
  correlation = ((length*XY)-(Xsum*Ysum))/sqrt(((length*XSq)-Xsum*Xsum)*(length*(Ysum*Ysum)-(Ysum*Ysum)))
  rSq = correlation * correlation
  ret = Table([('Slope', float), ('Intercept',float), ('Correlation', float), ('RSquared', float)])
  r = ret.append()
  r['Slope'] = slope
  r['Intercept'] = intercept
  r['Correlation'] = correlation
  r['RSquared'] = rSq
  return ret


def handshake_slope(table, ycol, xcol=None):
  '''Computes the slope between every point given.
     If xcol is None, it is generated starting as 0, 1, 2, 3, etc.

     For example:  Assume 5 points. 
     The slopes from points 1 to 2, 1 to 3, 1 to 4, 1 to 5, 2 to 3, 
     2 to 4, 2 to 5, 3 to 4, 3 to 5, and 4 to 5 are calculated.  
     The sum of those slopes are divided by the total number of 
     points to get an idea of the general trend.
       
       
     @param table:  The table to calculate the handshake slope on.
     @type  table:  Table
     @param ycol:   The y column to use.
     @type  ycol:   str
     @param xcol:   The x column to use.  This is optional.
     @type  xcol:   str
     @return:       A picalo table containing one cell: the calculated slope.
     @rtype:        Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating...', handshake_slope, table, ycol, xcol)
  check_valid_table(table, ycol)
  if xcol != None:
    check_valid_table(table, xcol)
  YPoints = table.column(ycol)
  if xcol != None:
    XPoints = table.column(xcol)
  else:
    XPoints = range(len(table))
  total=0
  runs=0
  counter=0
  for Point in XPoints:
    XPoint=Point
    YPoint=YPoints[counter]
    counter=counter+1
    inner_count=0
    for Set in XPoints:
      XSet=Set
      YSet=YPoints[inner_count]
      inner_count=inner_count+1
      if XPoint < XSet:
        PointSlope = (YSet - YPoint) / (XSet - XPoint)
        total = total + PointSlope
        runs=runs+1
  AverageSlope=total/runs
  return Table([('Handshake_Slope', float)], [[AverageSlope]])


