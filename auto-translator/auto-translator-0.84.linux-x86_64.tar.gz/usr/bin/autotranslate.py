#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Fri Aug 13 11:29:42 2010

@author: alfonsodg
"""
VERSION=0.80

import gtrans
import sys
import os
import yaml

Languages = gtrans.langs

#test file
__file__ = u'/home/alfonsodg/Devel/sahana/web2py/applications/eden/languages/es.py'
#languages (Origin and Destination)
__langO__ = u'en'
__langD__ = u'es'


def TransF():
#    print __file__
    prc=0
    In=open(__file__).readlines()
    Out=open(__file__+'.trans','w')
    for line in In:
        Trans = gtrans.translate(__langO__, __langD__,line).encode("utf-8")
        Out.write(Trans+'\n')
        prc+=1
        print u"Adv: %d "%((prc*100)/len(In))
    Out.close()


def FileO():
    global __file__
    __file__ = tkFileDialog.askopenfilename(title=u'Choose a file')
    FileLabel = Tkinter.Label(Ventana)
    FileLabel["text"] = "Selected : %s"%(__langO__)
    FileLabel.pack()
    MessageW('Press [OK] for start translation')
    TransF()
    MessageW()



def MessageW(Content=u'Translation Finish'):
    tkMessageBox.showinfo(title=u'Done',message=Content)


def VisualI():

    Area=Tkinter.Frame(Ventana)
    optionLabel = Tkinter.Label(Area)
    optionLabel["text"] = "Source Language"
    optionLabel.pack(side=Tkinter.LEFT)
    VarOrig = Tkinter.StringVar()
    comboBox = apply(Tkinter.OptionMenu, (Area, VarOrig) + tuple(Languages.values()))
    VarOrig.set("en")
    comboBox["width"] = 15
    comboBox.pack(side=Tkinter.LEFT)
    optionLabel = Tkinter.Label(Area)
    optionLabel["text"] = "Destination Language"
    optionLabel.pack(side=Tkinter.LEFT)
    VarDest = Tkinter.StringVar()
    comboBox = apply(Tkinter.OptionMenu, (Area, VarDest) + tuple(Languages.values()))
    VarDest.set("es")
    comboBox["width"] = 15
    comboBox.pack(side=Tkinter.LEFT)

    Area.pack()

    global __langO__
    global __langD__
    __langO__ = VarOrig.get()
    __langD__ = VarDest.get()

    FileB = Tkinter.Button(Ventana, text="File", command=FileO)
    FileB.pack()
    GoB = Tkinter.Button(Ventana, text="Go", command=MessageW)
    GoB.pack()

    Ventana.mainloop()

    sys.exit(0)



VisualM=False
if len(sys.argv) == 1:
    VisualM=True
    import Tkinter
    import tkFileDialog
    import tkMessageBox

    Ventana = Tkinter.Tk()
    Ventana.title("Choose Languages")
    Ventana["padx"] = 40
    Ventana["pady"] = 20

    VisualI()



try:
    __file__ = sys.argv[1]
    __langO__ = sys.argv[2]
    __langD__ = sys.argv[3]
except Exception,e:
    print e
    print 'Parameters Error!'
    print 'Usage: auto-translate.py filename OriginalLanguage DestinationLanguage'
    print 'Original and Destination Language using 2 (two) letter code'
    sys.exit(0)


Posw = __file__.find(u'web2py')
if Posw > 0:
    Web_path = __file__[:Posw]
else:
    Web_path = False

prc=0

if Web_path:
    sys.path.append(os.path.split(Web_path)[0])
    from web2py.gluon.languages import read_dict, write_dict
    dictionary = read_dict(__file__)
    for key, value in dictionary.iteritems():
        if key == value:
            dictionary[key]=gtrans.translate(__langO__, __langD__, value).encode("utf-8")
            prc+=1
            print u"Adv: %d "%((prc*100)/len(dictionary))
    write_dict(__file__, dictionary)
    print "DONE"
else:
    TransF()
    print "DONE"
