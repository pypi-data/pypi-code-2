#!/usr/bin/python3.1
# -*- coding: utf-8 -*-

#@author: Maik Wöhl
#@contact: logander4@icmail.com
#@copyright: Daemon Tutorials
#@license: MIT License
#@status: Stable Release
#@version: 2.1
#List of required files:
#-tkhelp.py
#-tkhelp_lang_de.py
#-tkh_splash2.py
#-test.gif
#-tkhelp_lang_de.py

import webbrowser # Webbrowser
import tkinter # Tk interface
import tkinter.scrolledtext # Tk scrolledText
import tkhelp_lang_de as LANG # Deutsche Sprachdatei
#import tkh_splash2 # SplashScreen
import tkh_splash3 # SplashScreen v3
import dt_tkobjects # Toplevel-Factory-Klasse


root = tkinter.Tk()
#splashParent = root
#tkh_splash2.splash(splashParent, "TKHelp 2.1", "test.gif", 500, 350)

print(LANG.startTKHmsg)
root.title(LANG.tkh_title)

splash = tkh_splash3.DtSplash(root, width=500, height=350)
splash.title("Tkhelp v2.1")
splash.set_image("test.gif")
splash.render()

dtObj = dt_tkobjects.dtObjects(root)

 
root["bg"] = "lightblue"

def copyright():
    print("\n(c) by Daemon Tutorials")
    print("\n Webadresse oeffnen?")
    openWebbrowser = input("Yes/No: ")
    if openWebbrowser == "yes" or openWebbrowser == "Yes" or openWebbrowser == "y":
        webbrowser.open("http://www.daemon-tuts.de")
    
           
def __buttonf():
    buttonObj = dtObj.createToplevel("Widget: Button", LANG.buttontxt, "button = tkinter.Button(master, text='Buttontext')\n button.pack()'", "button")
    dtObj.displayToplevel(buttonObj)
        
    
def __entryf():
    entryObj = dtObj.createToplevel("Widget: Entry", LANG.entrytxt, "entry = tkinter.Entry(master)\n entry.pack()", "entry")
    dtObj.displayToplevel(entryObj)
    
def __textf():
    textObj = dtObj.createToplevel("Widget: Text", LANG.textfieldtxt, "text = tkinter.Text(master)\n text.pack()", "text")
    dtObj.displayToplevel(textObj)
    
def __scrolledtextboxf():
    scrolledTextObj = dtObj.createToplevel("Widget: ScrolledText", LANG.scrolltexttxt, "scrolledtext = tkinter.scrolledtext.ScrolledText(master)\n scrolledtext.pack()", "scrolledtext")
    dtObj.displayToplevel(scrolledTextObj)
    
    
def __listboxf():
    listboxObj = dtObj.createToplevel("Widget: Listbox", LANG.listboxtxt, "listbox = tkinter.Listbox(master)\n listbox.pack()", "listbox")
    dtObj.displayToplevel(listboxObj)
    
def __radiobuttonf():
    radioObj = dtObj.createToplevel("Widget: Radiobutton", LANG.radiobuttontxt, "radiobtn = tkinter.Radiobutton(master)\n radiobtn.pack()", "radiobutton")
    dtObj.displayToplevel(radioObj)
    
def __checkboxf():
    pass

def __menubuttonf():
    pass

def __optionmenuf():
    pass

def __spinboxf():
    pass

def __menuf():
    pass

def __canvasf():
    canvasObj = dtObj.createToplevel("Widget: Canvas", LANG.canvastxt, "canvas = tkinter.Canvas(master, width=200, height=200)\n canvas.pack()", "canvas")
    dtObj.displayToplevel(canvasObj)

def __labelf():
    pass

def __scrollbarf():
    pass

    
#Definiere Frames
print(LANG.defFrames)
butframe = tkinter.Frame(root)
footer = tkinter.Frame(root)


#Definiere Buttons
print(LANG.defButtons)
button = tkinter.Button(butframe, text="Button", command=__buttonf)
entry = tkinter.Button(butframe, text="Entry", command=__entryf)
text = tkinter.Button(butframe, text="Text", command=__textf)
scrolledtextbox = tkinter.Button(butframe, text="Scrolled Textbox", command=__scrolledtextboxf)
listbox = tkinter.Button(butframe, text="Listbox", command=__listboxf)
radiobutton = tkinter.Button(butframe, text="Radiobutton", command=__radiobuttonf)
menubutton = tkinter.Button(butframe, text="Menubutton", command=__menubuttonf, state="disabled")
optionmenu = tkinter.Button(butframe, text="OptionMenu", command=__optionmenuf, state="disabled")
menu = tkinter.Button(butframe, text="Menu", command=__menuf, state="disabled")
spinbox = tkinter.Button(butframe, text="SpinBox", command=__spinboxf, state="disabled")
canvas = tkinter.Button(butframe, text="Canvas", command=__canvasf)
scrollbar = tkinter.Button(butframe, text="Scrollbar", command=__scrollbarf, state="disabled")
label = tkinter.Button(butframe, text="Label", command=__labelf, state="disabled")
checkbox = tkinter.Button(butframe, text="CheckBox", command=__checkboxf, state="disabled")

#Fuege Spalte 1 hinzu
print(LANG.stRow)
button.grid(row=1, column=1)
entry.grid(row=2, column=1)
text.grid(row=3, column=1)
menubutton.grid(row=4, column=1)
    
#Fuege Spalte 2 hinzu
print(LANG.ndRow)
scrolledtextbox.grid(row=1, column=2)
listbox.grid(row=2, column=2)
radiobutton.grid(row=3, column=2)
optionmenu.grid(row=4, column=2)

#Fuege 3 Spalte hinzu
print(LANG.rdRow)
checkbox.grid(row=1, column=3)
label.grid(row=2, column=3)
menu.grid(row=3, column=3)
scrollbar.grid(row=4, column=3)

#Fuege 4 Spalte hinzu
print(LANG.thRow)
spinbox.grid(row=1, column=4)
canvas.grid(row=2, column=4)

    
#Definiere Buttonbreite
print(LANG.defButtonWidth)
button["width"] = 15
entry["width"] = 15
text["width"] = 15
scrolledtextbox["width"] = 15
listbox["width"] = 15
radiobutton["width"] = 15
checkbox["width"] = 15
spinbox["width"] = 15
canvas["width"] = 15
scrollbar["width"] = 15
menu["width"] = 15
label["width"] = 15
optionmenu["width"] = 15
menubutton["width"] = 15
    
#Definiere Footer
print(LANG.defFooter)
copyright = tkinter.Button(footer, text=LANG.footer, command=copyright, relief="groove")
copyright.pack()
copyright["bg"] = "#CC6600" 
    
#Starte Endlosschleife
print(LANG.startLoop)
butframe.pack()
footer.pack(side=tkinter.BOTTOM)
butframe["bg"] = "lightblue"
footer["bg"] = "lightblue"
butframe["bd"] = "5px"
butframe["relief"] = "ridge"
print(LANG.startAppMSG)

try:
    root.mainloop()
except KeyboardInterrupt:
    print("\n\n^C recieve, close tkhelp...")
    root.destroy()
