from bottle import redirect


def cmd_fl(term):
    """Search among Flickr photos under Creative Commons license."""
    redirect('http://www.flickr.com/search/?q=%s&l=cc&ss=0&ct=0&mt=all&w=all&adv=1' % term)


def cmd_pep(term):
    redirect('http://www.python.org/dev/peps/pep-%0.4d/' % int(term))


def cmd_dj(term):
    """Django documentation search."""
    redirect(
        'http://docs.djangoproject.com/en/dev/search/?cx=009763561546736975936:e88ek0eurf4&'
        'cof=FORID:11&q=%s&siteurl=docs.djangoproject.com/en/dev/topics/db/models/' % term
    )
