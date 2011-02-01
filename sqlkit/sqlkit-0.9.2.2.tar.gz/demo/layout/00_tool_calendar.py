"""bricks/toolbutt calendar

icons can beadded directly to the IconFactory and called as a normal stock
image as in tb=cal

I Have ont understood how to use themes, thought
"""




factory = gtk.IconFactory()
#pixbuf = gtk.gdk.pixbuf_new_from_file('cal.gif')
pixbuf32 = gtk.gdk.pixbuf_new_from_file('cal32.png')
#pixbuf24 = gtk.gdk.pixbuf_new_from_file('cal24.png')
iconset = gtk.IconSet(pixbuf32)
#theme = gtk.IconTheme()
# theme = gtk.icon_theme_get_default()
# print ".has(%s): %s" % ('cal', theme.has_icon('cal'))
# print ".has(%s): %s" % ('gtk-add', theme.has_icon('gtk-add'))
# print iconset.get_sizes()
factory.add('calendar', iconset)
factory.add_default()
# print "DEF", gtk.icon_factory_lookup_default('cal')
# print "si sta: %s" % factory.lookup('cal')
# print ".has(%s): %s" % ('cal', theme.has_icon('cal'))
# factory.add_default()



lay = """
   {O tb=calendar tb=gtk-new }
   l=esempio_calendario
"""

l=Layout(lay)
w = l.show()

