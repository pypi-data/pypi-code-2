#!/usr/bin/env python
# coding: utf-8
from __future__ import division

'''Példaprogram a legkisebb négyzetek módszerére.

(Non)linear Least-squares (N)LLS

Írjuk meg a félkész függvényt és az original.dat adataival is futtassuk le. (Keressünk rá az egészít szórészekre.)

Ha a tanár mondja,
Futtassuk a program teljes változatát.
Indítsuk el a gnuplotot:
$ gnuplot
Ábrázoljuk a függvényértékeket:
gnuplot> plot "base.dat"
Ábázoljuk a kapott lineáris függvényt:
gnuplot> m=...
gnuplot> b=...
gnuplot> replot m*x + b
Illesszük a függvényértékeket a gnuplotban mx+b alakú függvénnyel:
gnuplot> fit m*x+b "base.dat" via m, b
(Próbálkozhatunk a*exp(b*x) alakú exponenciális függvénnyel is, azt is
rárajzolhatjuk az ábrára.)

/usr/share/doc/gnuplot-doc/gnuplot.html
/usr/share/doc/python2.3/html/index.html

Átmásolhatjuk fájlunkat a mail-re.

Otthon:
Hasonlítsuk össze a saját programunkat és a teljes változatot.

Horváth Árpád, 2006. december 2.'''


x=[	0,	1,	2]
y=[	0,	1,	1]

def linearis(x=x, y=y):
    """linearis(x, y) --> (m, b)

    x és y tartalmazza az x és y értékek listáját
    m és b a linearis kozelites meredeksége és tengelymetszete
    az y = mx + b szerint.

    m_szamlalo = n[xy] - [y][x]
    b_szamlalo = [x^2][y] - [x][xy]
    (mindkettőnél) nevezo= n[x^2] - [x]^2
    """
    
    n=len(x)
    if len(y) != n:
	print "Az x- és y-értékek száma különböző."
	return

    xsum = ysum = x2sum = xysum = 0
    for i in range(n): # 1-től n-ig
	xsum  += x[i]
	x2sum += x[i]**2
	ysum  += y[i]
	xysum += y[i]*x[i]

    nominator = n*x2sum - xsum**2
    m = n*xysum - ysum*xsum
    m /= nominator
    b = x2sum*ysum - xsum*xysum
    b /= nominator

    return  m, b

def load_dat(file="base.dat"):
    """Return with the values of x and y from the file.
    
    x values are in the first row, y values in the second.
    """

    f=open(file, "r")
    lines = f.readlines()
    f.close()
    
    x = []
    y = []
    for line in lines: 
	x1, y1 = line.split()
	x.append(float(x1))
	y.append(float(y1))

    return x, y

def make_dat(n, m=.5, b=1, file="base.dat"):
    import random
    lines = []
    for i in range(n):
	x = i
	y = m*x + b + (random.random()*2 - 1)
	lines.append( "%f\t%f\n" % (x,y) )

    f=open(file, "w")
    f.writelines(lines)
    f.close()
    
def plot(x,y,m,b):
    """Plot the values end the line."""

    try:
	import pylab
    except ImportError:
	print "***\nNem tudom kirajzolni, nincs pylab modul.\nTelepítse a matplotlib-et.\n***"
	return

    mx, mn = max(x), min(x)
    d= 0.2*(mx - mn)
    minx, maxx = mn-d, mx+d

    mx, mn = max(y), min(y)
    d= 0.2*(mx - mn)
    miny, maxy = mn-d, mx+d

    pylab.plot(x,y, "x")
    xx=pylab.linspace(minx, maxx, 1000)
    pylab.plot(xx, m*xx+b)
    pylab.axis([minx, maxx, miny, maxy])
    pylab.show()

if __name__ == "__main__":
    print "A programbeli x, y értékekkel"
    m, b = linearis()
    print m, b
    plot(x,y,m,b)

    print "A base.dat értékeivel"
    make_dat(20)
    x, y = load_dat()
    m,b = linearis(x,y)
    print "%f\t%f" % (m,b)
    plot(x,y,m,b)
