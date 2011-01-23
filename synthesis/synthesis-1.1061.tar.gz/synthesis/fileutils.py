
# The MIT License
# 
# Copyright (c) 2007 Suncoast Partnership 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
#import sys
import os
import glob
import copy
import shutil
import csv
from time import sleep as ossleep
import datetime
from synthesis.conf import settings
      
def sleep(sleepTime):
    print 'Sleeping for %s' % sleepTime
    ossleep(sleepTime)
    
def getSmartPath(baseDir, filePath):
    # 1st Try to open the filePath as a normal file path, if that works it should take precedence
    # 2nd if that doesn't work, try to open the path as a subdirectory of the basepath
    # 3rd if that doesn't work try to create the path
    # lastly, if that doens't work, raise a hard error
        if os.path.exists(filePath):
            return filePath
        else:
            newPath = os.path.join(baseDir, filePath)
            if os.path.exists(newPath):
                return newPath
            else:
                try:
                    os.makedirs(newPath)
                except OSError:
                    raise OSError
            
def checkPath(filePath):
    # first check if the path exists
    if os.path.exists(filePath):
        # nothing to do return 0
        return 0
    # if it doesn't exist, try to create it
    else:
        try:
            os.makedirs(filePath)
            if os.path.exists(filePath):
                return 0
            else:
                raise
        except:
            raise

def keyToDict(listVals):
    dict={}
    for key in range(0,len(listVals)):
        dict.setdefault(listVals[key],key)
    return dict
    
def stripData(record, delimiter='\n'):
    #print "ready to strip bad data"
    record = record.split(delimiter)
    record = record[0]
    #record = self.unquoteString(record, findChar='"')
    return record

def unquoteList(parts=[], findChar='"'):
    newList = []
    for item in parts:
        item = unquoteField(item, findChar='"')
        newList.append(item)
    return newList
    
def unquoteField(field, findChar='"'):
    newField = ''
    newField = field.replace(findChar, '')
    newField = newField.replace(findChar, '')
    x = copy.deepcopy(newField)
    return x
            
def unquoteString(record="", findChar='"'):
    posFind = record.find(findChar)
    while not posFind == -1:
        record = record.replace(findChar, '')
        posFind = record.find(findChar)
    return record
    
def cleanRecord(record, delimitter, findChar, replaceChar, startPos=0):
    ''' this function takes the input record (csv record) and 
    searches for a delimiter (") at the extremes of the record
    and replaces the findChar with a replaceChar in the substring
    between the delimited chars.'''
    #print "Before Cleaning Record is: " + record
    pos1Find = record.find(delimitter, startPos)
    if pos1Find == -1: # quick out, not found exit out with original record
        return record
    pos2Find = record.find(delimitter, pos1Find + 1)
    if pos2Find == -1: # quick out, not found exit out with original record
        return record
    badChars = record[pos1Find:pos2Find + 1]
    
    goodChars = badChars.replace(findChar, replaceChar)
    
    newRecord = record[0:pos1Find] + goodChars + record[pos2Find+1:len(record)]
    
    # recursive call to ourself maybe there is more data that's fd up.
    pos3Find = newRecord.find(delimitter, pos2Find)
    if pos3Find == -1: # quick out, not found exit out with
        #print "After Cleaning Record is: " + newRecord
        return newRecord
    else:
        #print "Before 2nd Cleaning Record is: " + newRecord
        newRecord = cleanRecord(record=newRecord, delimitter=delimitter, findChar=findChar, replaceChar=replaceChar, startPos=pos2Find+2)
    
    return newRecord
    
def parseRecord(record, delimiter=","):
    #print "Ready to parse a record..."
    #print record
    recParts = []
    # intakes file is delimited with "\r" and outcomes is del with "\r\n"
    findThis = "\r\n"
    if record.find(findThis) == -1:
        record = stripData(record)
    else:
        record = stripData(record, findThis)
    
    recParts = record.split(delimiter)
    
    return recParts

def suckFile2(filename):
    records = []
    print "Ready to suck file2 in %s" % filename
    try:
        reader = csv.reader(open(filename, "rb"))
        for row in reader:
            records.append(row)
    except:
        print "ERROR: filename: %s not found.  Please investigate" % filename
            
    #print 'sucked in %s records' % reader.line_num
    print 'sucked in %s records' % len(records)
    
    return records

def suckFile(filename):
    records = []
    print "Ready to suck file in %s" % filename
    try:
        file = open(filename, 'r')
    except:
        print "ERROR: filename: %s not found.  Please investigate" % filename
         
    records = file.readlines()
        
    print 'sucked in %s records' % len(records)
    
    return records

def pushIntoDict(dictName, theDict, theKey, theRow, appendRow=False):
    rc = 0
    tmpList = []
    # first check to see if the dictionary has the key already
    if theDict.has_key(theKey):
        rc = 0
        #print 'Key: %s already in Dictionary: %s' % (theKey,dictName), theRow
        #print
        #print 'Existing Value is: ', theDict[theKey]
        #print '*'*80
        if appendRow == True:
            rowVal = theDict[theKey]
            #print "Found existing row %s for key: %s and appending row data %s" (theKey, rowVal, theRow)
            rowVal.append(theRow)
            theDict[theKey] = rowVal
            rc = 2
        else:
            "problem here"
            #failedDictAdd[dictName] += 1
    else:
        if appendRow == True:
            tmpList.append(theRow)
            theDict[theKey] = tmpList
        else:
            theDict[theKey] = theRow
            
        rc = 1
    return rc

def dumpObjToFile(dumpObject, filename):
    # function to dump some type of object to a file (normally a debug list to a file)
    print "dump File Processing"
    
    f = open(filename, 'w')
    
    if dir(dumpObject).count('__iter__') > 0:
        # we have an iterator, loop through it
        #for lines in dumpObject:
        f.writelines(dumpObject)
    else:
        f.write(str(dumpObject))
        
    # close the file
    f.close()

def grabFiles(directoryToProcess):
    print "Getting Files"
    validFiles = []
    # adding file sucking capability
    files = glob.glob(directoryToProcess)
    # pull list of files
    for file in files:
        print "processing: %s" % file
    
        validFiles.append(file)
    
    print 'Done Grabbing Files'
    return validFiles

def getTimeStampedFileName(unstamped_file_path):
    '''Simply extract the name of a file from a path string, timestamp the file name, and return a file name string with the modification.'''
    if settings.DEBUG:
        print "unstamped_file_path in getTimeStampedFileName is: ", unstamped_file_path
    (old_file_path, old_file_name) = os.path.split(unstamped_file_path)
    old_file_name_prefix = os.path.splitext(old_file_name)[0]
    old_file_name_suffix = os.path.splitext(unstamped_file_path)[1]
    new_file_name_prefix = old_file_name_prefix + str(datetime.datetime.now())
    stamped_file_name = new_file_name_prefix + old_file_name_suffix
    stamped_file_name = stamped_file_name.replace(' ', '_')
    if settings.DEBUG:
        print "stamped_file_name in getTimeStampedFileName is: ", stamped_file_name
    return stamped_file_name

def getUniqueFileNameForMove(attempted_file_name, destination_directory):
    '''Returns a new unique timestamped file name string to use at destination_directory indicated.'''
    
    attempted_file_path = destination_directory + "/" + attempted_file_name
    if settings.DEBUG:
        if os.path.isfile(attempted_file_path):    
            print "output location", attempted_file_path, "already exists"
    #print "attempted_file_path before getTimeStampedFileName", attempted_file_path       
    stamped_file_path = getTimeStampedFileName(attempted_file_path)
    #print "stamped_file_path in getUniqueFileNameForMove", stamped_file_path
    if os.path.isfile(stamped_file_path):
        print "The renamed file is also already there, please check this out."
    #stamped_pathname is a whole path, so just return the filename part without path
    (file_path, unique_file_name) = os.path.split(stamped_file_path)
    #return just the filename
    return unique_file_name

def moveFile(source_file_path, destination_directory):
    '''Move a file path to a destination directory.  But first, test if the destination exists.  If not make it.  Also timestamp it.'''
    try:
        if not os.path.exists(destination_directory):
            os.mkdir(destination_directory)
        (source_file_path_prefix, source_file_name) = os.path.split(source_file_path) 

        #ECJ20100829 rename the file over in tmp, because I don't want to renamed file to trigger an inotify event for monitor() before it's moved to an unlistened dir
        temp_file_path = os.path.join(settings.BASE_PATH, 'tmp', source_file_name)
        try:
            os.remove(temp_file_path)
        except OSError:
            pass
        shutil.move(source_file_path, temp_file_path)
                
#                if settings.DEBUG:
#                    print "temp_filepath is: ", temp_filepath
        (temp_file_path_prefix, temp_file_name) = os.path.split(temp_file_path)
        timestamped_temp_file_name = getUniqueFileNameForMove(temp_file_name, destination_directory)
        timestamped_temp_file_path = os.path.join(temp_file_path_prefix, timestamped_temp_file_name)
        shutil.move(temp_file_path, timestamped_temp_file_path)
        try:
            shutil.move(timestamped_temp_file_path, destination_directory)
        except shutil.Error:# as detail:
            raise
            #print detail
#                if settings.DEBUG:
#                    print "new temp filepath should be: ", new_temp_filepath
#                    if os.path.isfile(new_temp_filepath):
#                        print "and it is"
#                    else:
#                        print "but it isn't"
    except:
        raise
   
def renameFile(source, dest):
    # SBB20100421 rename was only doing a copy to new name, leaving old file, wrong.  Fixed to remove source
    try:
        shutil.copy(source, dest)
        deleteFile(source)
    except:
        pass
    
def copyFile(source, dest):
    shutil.copy2(source, dest)

def deleteFile(fileDelete):
    try:
        os.remove(fileDelete)
    except:
        print "\T\TFAILURE:Deletion of file %s failed" % fileDelete * 3
        raise
    print "SUCCESS: Deletion of file %s succeeded" % fileDelete
    
def backupFile(project):
    # copy the file to a backup filename we are creating a new copy of the file
    copyFile(project, project + ".bak")    
    
def makeBlock(wording, numChars=0):
    # SBB20090902 why pass in the number of characters (fixed block sizes)
    if numChars == 0:
        numChars = len(wording)
        
    if len(wording) >= numChars:
        numChars = len(wording) + 4
    numSpaces = (numChars - (len(wording) + 2)) / 2
    oddSpacing = (numChars - len(wording)) % 2
    print numChars * ("*")
    print "*" + " " * numSpaces + wording + " " * numSpaces + oddSpacing * (" ") + "*"
    print numChars * ("*")

def sortItems(incomingList, colToSort=''):
    from operator import itemgetter
    # this is a single operation to sort a list of dictionaries
    return sorted(incomingList, key=itemgetter(colToSort))
