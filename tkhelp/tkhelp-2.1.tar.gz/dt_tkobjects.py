#!/usr/bin/python3.1

# tkhelp TKObject class
import tkinter
import tkhelp_lang_de as LANG

class dtObjects():
    def __init__(self, parent):
        self.parent = parent
        
    def createExample(self, type):
        if type == "button":
            self.example = tkinter.Button(self.master, text="Hello World!")
            self.example.pack()
            
        elif type == "entry":
            self.example = tkinter.Entry(self.master, text="Hello World!")
            self.example.pack()
            
        elif type == "canvas":
            self.example = tkinter.Canvas(self.master, width=200, height=200)
            self.example.pack(padx=5, pady=5)
            self.example.create_oval(50, 50, 150, 150, fill="orange", width=3)
            self.example.create_line(50, 150, 150, 50, width=3)
            self.example.create_line(50, 50, 150, 150, width=3)
            
        elif type == "radiobutton":
            auswahl = ["Berlin", "Moskau", "Paris", "Honolulu"]
            var = tkinter.StringVar()
            var.set("Moskau")
    
            for a in auswahl:
                self.example = tkinter.Radiobutton(self.master, text=a, value=a, variable=var)
                self.example.pack(side=tkinter.BOTTOM, anchor="w")
                
        elif type == "listbox":
            self.example = tkinter.Listbox(self.master)
            self.example.pack(side=tkinter.BOTTOM)
            eintraege = ["Berlin", "London", "Hawai", "Paris"]
    
            for stadt in eintraege:
                self.example.insert("end", stadt)
                
        elif type == "scrolledtext":
            self.example = tkinter.scrolledtext.ScrolledText(self.master)
            self.example.pack(padx=5, pady=5)
            self.example.tag_config("u", underline=True)
            self.example.insert("end", LANG.scrolltexttxt2, "u")
            
        elif type == "text":
            self.example = tkinter.Text(self.master)
            self.example.pack(padx=5, pady=5)
    
        else:
            self.example = tkinter.Label(self.master, text="Kein Beispiel verfuegbar!")
            self.example.pack()
    
    def createToplevel(self, title, desc, source, type):
        self.master = tkinter.Toplevel(self.parent)
        self.master.withdraw() # The API User can display the Toplevel
        self.master.title(title)
        
        self.desc = desc
        self.descLabel = tkinter.Label(self.master, text=self.desc)
        self.descLabel.pack()
        
        self.source = source 
        self.sourceLabel = tkinter.Label(self.master, text=self.source)
        self.sourceLabel.pack()
        self.sourceLabel.config(bg = "white")
        
        self.execTXT = LANG.exectxt
        self.execLabel = tkinter.Label(self.master, text=self.execTXT)
        self.execLabel.pack()
        
        self.createExample(type)
        
        
        return self.master
        
    def displayToplevel(self, parent):
        self.userParent = parent
        self.userParent.deiconify()
