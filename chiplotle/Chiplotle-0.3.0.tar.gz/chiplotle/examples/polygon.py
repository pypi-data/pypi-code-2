from chiplotle import *

subshapes = [Rectangle((0, 0), 2000, 800), 
   Circle((-400, 0), radius = 200), 
   Circle((400, 0), radius = 200)]
p = Polygon((0, 0), subshapes, filled=True, pen=1)
print 'subcommands:', p._subcommands

io.view(p)
