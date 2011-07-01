import re

uri = re.compile(
    r"(((?P<protocol>[a-zA-Z][0-9a-zA-Z+\\-\\.]*):)?/{0,2}[0-9a-zA-Z;/?:@&=+$\\.\\-_!~*'()%]+)?(#[0-9a-zA-Z;/?:@&=+$\\.\\-_!~*'()%]+)?")

expression = re.compile(
    r"(['\"](?P<title>[^'\"]+)['\"]:)?"
    "(?P<uri>(([a-zA-Z][0-9a-zA-Z+\\-\\.]*:)?/{0,2}[0-9a-zA-Z;/?:@&=+$\\.\\-_!~*'()%]+[0-9a-zA-Z;/?@&=+$\\.\\-_!~*'()%]+)?"
    "(#[0-9a-zA-Z;/?:@&=+$\\.\\-_!~*'()%]+[0-9a-zA-Z;/?@&=+$\\.\\-_!~*'()%])?)"
    "(:?['\"](?P<description>[^'\"]+)['\"])?")

def pack(uri, title, description):
    u = uri

    if title:
        u = '"%s":%s' % (title, u)

    if description:
        u = '%s:"%s"' % (u, description)

    return u

def unpack(u):
    """
    Unpacks a string on the form:

        "Title":URI:"Description"

    Both title and description are optional. Single or double quotes
    are allowed.

    First, we demonstrate unpacking of URIs.
    
       >>> unpack(u"http://www.google.com")
       (u'http://www.google.com', None, None)

       >>> unpack(u'www.google.com')
       (u'www.google.com', None, None)

       >>> unpack(u'"Google":http://www.google.com')
       (u'http://www.google.com', u'Google', None)
       
       >>> unpack(u'"Google":http://www.google.com:"Google is a search engine"')
       (u'http://www.google.com', u'Google', u'Google is a search engine')

       >>> unpack(u'"Google":http://www.google.com:8080:"Google is a search engine"')
       (u'http://www.google.com:8080', u'Google', u'Google is a search engine')

       >>> unpack(u'"Google":http://www.google.com:8080#bookmark-1:"Google is a search engine"')
       (u'http://www.google.com:8080#bookmark-1', u'Google', u'Google is a search engine')

       >>> unpack(u'"Google":http://www.google.com:8080')
       (u'http://www.google.com:8080', u'Google', None)

    We also support non-URI, i.e. internal links:

       >>> unpack(u'"Fruits and greens":fruits-and-greens')
       (u'fruits-and-greens', u'Fruits and greens', None)

       >>> unpack(u'"Fruits and greens":fruits-and-greens:"Healthy ingredients."')
       (u'fruits-and-greens', u'Fruits and greens', u'Healthy ingredients.')

       >>> unpack(u'"Fruits and greens":/fruits-and-greens')
       (u'/fruits-and-greens', u'Fruits and greens', None)
    """

    match = expression.match(u)

    if match is None:
        raise ValueError("Unable to parse %s" % u)

    uri = match.group('uri')
    title = match.group('title')
    description = match.group('description')
        
    return (uri, title, description)
        

     
