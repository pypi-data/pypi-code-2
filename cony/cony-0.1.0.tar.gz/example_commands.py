from bottle import redirect

def cmd_fl(term):
    """Search among Flickr photos under Creative Commons license."""
    redirect('http://www.flickr.com/search/?q=%s&l=cc&ss=0&ct=0&mt=all&w=all&adv=1' % term)

