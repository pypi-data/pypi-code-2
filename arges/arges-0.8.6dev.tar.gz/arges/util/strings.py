# -*- coding: latin-1 -*-

"""strings -  this module provides helper function to work with strings

@author: Adrián Deccico
"""

import re

def replaceIfNotEscapedCharacter(s, old, new):
    """ this function replace a possible escaped character within a string """
    if len(old) > 1:
        raise NameError, 'The substring to replace should have a len of 1 byte'
    ret = ""
    i = 0
    while i < len(s):
        if s[i] != old:
            ret = ret + s[i]
        else:
            ret = ret + new
            if i+1 < len(s) and s[i+1] == old:
                ret = ret + s[i+1]
                i = i + 1
        i = i + 1

    return ret

def processArgs(args):
    args = args.split(" ") #transform the string in a list
    args_processed = []
    for str in args:
        #cut the " but look if there any "" (a escaped ")
        args_processed.append(replaceIfNotEscapedCharacter(str, '"', ""))
    return args_processed

def rtrim(string):
    return re.sub(r"""[\s]*$""", "", string)

def ltrim(string):
    return re.sub(r"""^[\s]*""", "", string)
                
def trim(string):
    string = rtrim(string)
    string = ltrim(string)
    return string

def cutSuffix(string, suffix = None):
    """cut from a string, its suffix"""
    if suffix is None:
        # I just want the string without any dots.
        return string.split('.')[0]
    
    if string.endswith(suffix):
        string = string[:len(string)-len(suffix)]
        
    return string
    
def formatTestParameter(param):
    """return the correct format of a parameter. That is now a valid regex pattern
    
    pre, param is a valid parameter
    """
    return "\\" + param 
                
def simpleParse(str):
    """ It returns a dict where the keys are in the form of '-<char>' and
        the values are any value"""
        
    reg = re.compile('-\w+\s')
    dict = {}
    
    commands  = reg.split(str)
    try:
        commands.remove("")
    except:
        # Cool, no "" value
        pass
    
    params = reg.findall(str)
    
    for x, y in zip(params, commands):
        dict[x.strip()] = y.strip()
    return dict

def extensionIs(line, extention):
    return line.split(".")[-1] == extention

def removeComment(line):
    """remove comment of the line"""
    return re.sub(r"""\B#.*$""", "", line)

def getExtension(line):
    return line.split(".")[-1].strip()


def clean_line(line):
    """
        This function removes the comment the line and then it strips it.
    """ 
    line = removeComment(line)
    return line.strip()
            