"""Próbálkozások"""


def plot_text(xx=0.5,yy=0.9):
    ax=subplot(111)
    x=arange(1,11)
    y=5*x**(-3)
    loglog(x,y)
    text(xx, yy,
	"szoveg",
	verticalalignment="top",
	transform=ax.transAxes)


