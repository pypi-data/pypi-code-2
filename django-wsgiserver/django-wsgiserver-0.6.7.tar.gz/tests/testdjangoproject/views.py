from django.http import HttpResponse, HttpResponseRedirect

def hello(request):
    return HttpResponse(
        """<html><body><h2>hello django-wsgiserver</h2>
        <h3>Tests</h3>
        <ul>
        <li> <a href="/admin/">Check the default admin media service</a></li>
        </ul>
        </body></html>""")

