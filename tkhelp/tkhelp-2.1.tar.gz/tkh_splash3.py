import tkinter
import math

#################
#Hilfsfunktionen#
#################

# Zentrieren
def center(widget):
    screen_width  = int(widget.winfo_screenwidth())
    screen_height = int(widget.winfo_screenheight())

    xpos = (screen_width - widget.cget("width")) / 2
    ypos = (screen_height - widget.cget("height")) / 2
	
    return [xpos, ypos]
    

def fadeout(toplevel, alpha):
    try:
        toplevel.wm_attributes("-alpha", next(alpha))
        toplevel.after(10, fadeout, toplevel, alpha)
    except StopIteration:
        if toplevel.dt_splash == False:
            raise splashError("imageError")
            
        toplevel.destroy()
        toplevel.master.deiconify()


class splashError(Exception):
    def __init__(self, value, **args):
        self.type = value
        if type == "titleError":
            self.value = repr("titleError: Your Title must be under 21 Chars! Your length: "+str(len(title)))
        elif type == "imageError":
            self.value = repr("imageError: You don't have specified an image-URL. Make it with set_image(string url)!")
        
    def __str__(self):
        return self.value


######
#Main#
######

class DtSplash(tkinter.Toplevel):     

    def __init__(self, master, **kwargs):
        tkinter.Toplevel.__init__(self, master, kwargs)
        # Die Referenz waere demnach also self.master
        self.master.withdraw()
        self.overrideredirect(True) 
        
        self.canvas = tkinter.Canvas(self, bg="white") # Canvas
            
            
        centerVars = center(self)
        self.wm_geometry("%dx%d+%d+%d" % (self.cget("width"), centerVars[1], centerVars[0], centerVars[1]))
 
    def set_image(self, image_url):
        self.photo = tkinter.PhotoImage(file=image_url) # Das Foto
            
    def render(self):
        
        self.canvas.create_image(0,0, image=self.photo, anchor=tkinter.NW) # Bild
        self.dt_splash = True
      
      
        # If title under 20 Chars?
        if len(self.title()) <= 20:
            self.canvas.create_text(250,50, text=self.title(), font="30") # Titel
        else:
            raise splashError("titleError", title=self.title())
        
        
        self.canvas.pack(fill="both", expand=True)
        
        alpha = (math.sqrt(a) / 10.0 for a in range(100, 0, -1))
        def fading():
            fadeout(self, alpha)
            
        self.after(2*1000, fading)
 
