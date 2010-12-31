import math

import cairo


surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)

cx = cairo.Context(surface)
cx.set_source_rgb(1, 1, 1)
cx.paint()

cx.set_source_rgb(0, 0, 0)

label = 'rotate'
x, y = 200, 300
px = max(cx.device_to_user_distance(1, 1))
cx.arc(x, y, 2 * px, 0, 2 * math.pi)

xb, yb, width, height, xa, ya = cx.text_extents(label)

cx.translate(x, y)
cx.rotate(math.radians(60))
cx.move_to(-xb, -yb)
cx.show_text(label)
cx.rectangle(0, 0, width, height)
cx.stroke()

surface.write_to_png('rotate.png')
