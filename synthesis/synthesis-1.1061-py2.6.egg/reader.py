'''Parser interface for input data.  Reads in data from wire formats and \
stores them persistently.'''
'''The MIT License
 
 Copyright (c) 2007 Suncoast Partnership 
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.''' #IGNORE:W0105

from zope.interface import Interface

class Reader(Interface): #IGNORE:W0232
    '''Interface documentation'''

    def read(self, input_file): #IGNORE:E0213
        '''Method interface for reading in an input file to memory'''
        # Note that there is no self argument, since it's just an interface
    
    def process_data(self): #IGNORE:E0213
        '''Method interface for processing, translating and storing\
        data read into memory by reader()'''
