"""Bricks/menu_entry

"""

lay = """
   C=mare2 C=mare3 Ce=montagna2 
"""


l = Layout(lay,opts="V")

def key_press_cb(wdg, ev):
    print wdg, ev
    for i in dir(ev):
        print i, getattr(ev, i)

def visibility_cb(wdg, ev):
    for i in dir(ev):
        print i, getattr(ev, i)


monti = 'M.te Bianco, Zebru, Gran Combin'
l.prop(
    ('C=mare2', 'items', 'capri\nla maddalena\ncuba'),
    ('C=mare3', 'items', 'capri\nla maddalena\ncuba'),
    ('Ce=montagna2', 'items', monti.replace(", ", "\n")),
    )

w = l.show()
l.connect(
    ('C=mare2', 'key_press_event', key_press_cb),
    ('C=mare2', 'visibility-notify-event', visibility_cb)
    )
#l.w['C=mare2'].connect()
m = w['C=mare2']
m.set_active(1)

