#!/util/bin/python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2006 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage: %prog [options] <input file>

Load an R library, and pass in options from the command line to that library

This is an adapter that should be used by python clients to R code.

If you want to pass in a vector as an argument, encode it as a comma seperated string "A,B,C".

If you want to pass in a list as an argument, pass in a python list ["A", "B", "C"]
"""

import sys
import optparse
import mpgutils.utils
import os
import subprocess

def callRscript (lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True):
    """Call the R script via Rscript.  If output is captured, it is returned, otherwise return the return code."""
    strCall=generateCall(lstLibraries, methodName, dctArguments)
    if (bVerbose): print ("Calling:  " + strCall)
    #os.system(strCall)
    if (captureOutput):
        output=subprocess.Popen(strCall, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0] 
        return (output)
    else:
        retCode=subprocess.Popen(strCall, shell=True).wait()
        return (retCode)
    
def generateCall (lstLibraries, methodName, dctArguments):
    
    strCommand="Rscript"
    
    
    #add library calls
    for library in lstLibraries:
        libCommand="-e 'library(" + library + ")'"
        strCommand=strCommand + " " +libCommand
     
    #encode method
    methodCommand="-e '" + methodName +"("
    
    argNames=dctArguments.keys()
    argValues=dctArguments.values()
    
    for i in range(len(argNames)):        
        methodCommand=methodCommand + argNames[i] + "="
        value=encodeValue(argValues[i])
        methodCommand=methodCommand+value
        if i != (len(argNames)-1):
            methodCommand=methodCommand+","
    methodCommand=methodCommand+")'" #finish method call
    
    strCommand=strCommand+" " +methodCommand
    return (strCommand)
    
def encodeValue (value):
    if value==None: return ("NULL")
    if isinstance (value, bool):
        if (value==True): return ("T")
        if (value==False): return ("F")
    
    if isinstance(value, int):
        return str(value)
    
    if isinstance(value, float):
        return str(value)

    if isinstance(value, str):
        if detectCommaSepStringAsVector(value):
            return encodeCommaSepStringAsVector(value)
        
        return "\""+value+"\"" #encode as a string
    
    if isinstance(value, list):
        a=str(value)
        
        a=a.replace("[", "")
        a=a.replace("]", "")
        a=a.replace("'", "\"")
        value="list("+a+")"
             
    #for any type not yet specificed here...
    return value


def detectCommaSepStringAsVector(value):
    valueLength=len(value.split(","))
    if valueLength==1:
        return False
    return True
 
def encodeCommaSepStringAsVector(commaStr):
    lstStrings=commaStr.split(",")
    resultStr="c("
    for l in lstStrings:
        l="\"" + l + "\","
        resultStr=resultStr+l
    
    resultStr=resultStr.rstrip(",")
    resultStr=resultStr+")"
    return (resultStr)
