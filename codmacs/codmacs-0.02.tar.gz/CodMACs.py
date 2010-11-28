#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Framework for Metaprogramming (Python Implementation)"""

__author__ = "mRt (martincerdeira@gmail.com)"
__version__ = "0.02"
__date__ = "$Date: 2009/09/17 17:47 $"
__license__ = "GPL v3"

import sys 
import os
import difflib

__fo = None
scr_indent = 0

# CodMACs Main Functions
# Editing this could make CodMACs crash or work improperly

class Csorted(object):
    def __init__(self, cdict):
        self.cdict = cdict

    def _findIndex(self, index):
        for i in self.cdict.values():
            if index == i.Index:
               return i

    def __iter__(self):
        e = 1
        for i in self.cdict.values():
            yield self._findIndex(e)
            e += 1

def reChop(v):
    return v.replace(chr(10),"").replace(chr(13),"")
    
def reChop2(v):
    return v.replace("\n","/n").replace(chr(10),"").replace(chr(13),"")   

def cmWrite(v):
    global __fo
    global scr_indent
    __fo.write(" " * scr_indent + v + chr(10))


def chr34(n):
    return chr(34) * n
        
def codmacsDiff(f1,f2):
    fi = open(f1,"r") 
    fo = open(f2,"r") 
    lf1 = fi.readlines()
    lf2 = fo.readlines()
    fi.close()
    fo.close()
    # Old (bad?) idea, maybe someday...
    #s = difflib.SequenceMatcher(None, lf2, lf1)    
    #fi = open(f2 + ".patch","w")     
    #for tag in s.get_opcodes():
    #    if tag[0] == "delete":  
    #        fi.write(str(tag[0]) + " : " + str(lf2[tag[1]:tag[2]]))
    #    if tag[0]=="insert":
    #        fi.write(str(tag[0]) + " : " + str(lf1[tag[3]:tag[4]])+ chr(10)) 
    #    if tag[0] == "replace":
    #        fi.write(str(tag[0]) + " : " + str(lf2[tag[1]:tag[2]]) + " con " +  str(lf1[tag[3]:tag[4]]))             
    #fi.close()
    
    # Generates a HTML with differences
    html = difflib.HtmlDiff()   
    h = html.make_file(lf2,lf1)    
    fi = open(f2 + ".html","w")   
    fi.write(h)
    fi.close()
    
        
def showHelp():         
    print " _____           ____  ___ ___  _____     "
    print "/  __ \         | |  \/  |/ _ \/  __ \    "
    print "| /  \/ ___   __| | .  . / /_\ \ /  \/___ "
    print "| |    / _ \ / _` | |\/| |  _  | |   / __|"
    print "| \__/\ (_) | (_| | |  | | | | | \__/\__ \\"
    print " \____/\___/ \__,_\_|  |_|_| |_/\____/___/"
    print "                         powered by python"
    print "-------------------------------------"
    print "Usage: CodMACS.py <action> <cn> <host> <user> <pwd> <database> [<table>] [<source_file_name>] [<destination_file_name>]"    
    print "-------------------------------------" 
    print "   action:" 
    print "      h Show this Help"
    print "      s Show only"   
    print "      v Create (verbose)"         
    print "      r Create only"       
    print "-------------------------------------"
    print "   cn:"
    print "      CONECTION TYPE (default MySQL)" 
    print "      MySQL"
    print "      MSSQL"
    print "      ORACLE"      
    print "      POSTGRE"
    print "      FIREBIRD"       
    print "      VOID (do not use any table!)"
    print "-------------------------------------"       
        
if len(sys.argv) <= 6 or sys.argv[1] == "h":
    showHelp()       
else:
    # Required Command line arguments
    action = sys.argv[1]
    cn = sys.argv[2]         
    shost = sys.argv[3]
    suser = sys.argv[4]
    spasswd = sys.argv[5]
    sdb = sys.argv[6]
    # Optional Command line arguments
    stabl = ""
    f1 = ""
    f2 = ""
    scr_indent = 0 # Indentation char counter
                
    if len(sys.argv) >=8:     
        stabl = sys.argv[7]
    if len(sys.argv) >=9:     
        f1 = str(sys.argv[8])
        f1 = f1.replace(chr(10),"").replace(chr(13),"")
    if len(sys.argv) >= 10:     
        f2 = str(sys.argv[9])    
        f2 = f2.replace(chr(10),"").replace(chr(13),"")    
    
    if action=="r" or action=="v":             
        if f1=="" or f2=="":
            print "Must specify source and destination file"    
            raise SystemExit   
       
        print "Parsing: " + f1 + " to: " + f2 + " ..."

    ############################
    # Here starts the magic... #
    ############################
    
    # Dynamic Function String    
    func = "def codmacsmain():\n"    
    from CMFunc import * # User Defined functions
    func += '    import CMCore \n'     
    func += '    files = CMCore.codFile("' + str(f1) + '","' + str(f2) + '") \n' 
    func += '    table = CMCore.codTable("' + shost + '","' + suser +'","' + spasswd + '","' + sdb + '","' + stabl + '","' + action + '","' + cn + '") \n'        
    func += "    buf = " + chr(34) + chr(34) + "\n" 
    if action=="r" or action=="v":
        func += "    global __fo \n"
        func += "    global scr_indent \n"        
        
        # Check if file exists and ask for user interaction
        resp = ""
        if os.path.exists(f2):                    
            while resp.lower() not in ("yes","no","y","n"):
                resp = raw_input("Destination File: " + f2 + " exists, replace it? (yes/no) ")       
            
        if resp.lower() in ("no","n"):                    
            func += '    __fo = open("tmp","w") \n'  
            func += "    fdiff = True\n"
            lfdiff = True # Local fdiff            
        else:
            func += '    __fo = open("' + f2 + '","w") \n'  
            func += "    fdiff = False\n"
            lfdiff = False     
        

    if action=="r" or action=="v": # Only if you create, else, prints info (in CMCore.py)
        fi = open(f1,"r")          
        st_py = False  # In python tag flag                     
        for lin in fi:            
            if str(lin).find("<scr_python>") != -1:
                scr_indent = str(lin).find("<scr_python>")
                func += "    scr_indent=" + str(scr_indent)  + "\n"
                st_py = True                                    
            elif str(lin).find("</scr_python>") != -1:                                                                                 
                st_py = False                           
            else:
                if st_py:       
                    c = str(lin)[scr_indent:]                                
                    func += "    " + c
                else:                                      
                    func += "    __fo.write(" + chr34(3) + reChop(str(lin)) + " " + chr34(3) + " + chr(10)" + ")\n"
                                                       
        fi.close()                                          
                
    func += "\n"                 
    if action=="r" or action=="v":           
        func += "    __fo.close() \n"
        if lfdiff:
            func += "    if fdiff:\n"             
            func += '        codmacsDiff("tmp",f2)  \n'   
            func += '        os.remove("tmp")\n'        
                                        
    func += "    return buf"    
        
    # Saves the function in a file for DEBUG
    #fo = open("func.debug","w")
    #fo.write(func)
    #fo.close()

    eval(compile(func, "<string>", "exec"))          
    codmacsmain()
    
    print "Done."
                  
