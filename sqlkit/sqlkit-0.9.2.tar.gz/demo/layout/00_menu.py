"""Bricks/menu_button

"""

simple_menu = """
 {B m=_File  } 
"""



l = Layout(simple_menu, opts="Vs")
w = l.show()

def di_ciao(*args):
    print 'ciao'

l.menu('m=_File',
    ('fine' , 'activate', gtk.main_quit),
    ('inizio' , 'activate', di_ciao, ),
    ('-' , None, ),
    ('gtk-open' , 'activate', lambda wid: gtk.main_quit())
    )   

