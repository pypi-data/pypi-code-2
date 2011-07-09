from django.utils import simplejson
from apps.location.models import City
#from apps.user import login_required

def cities_list(app):
    '''Return cities list'''
    cities = City.all().order("name").count(10)
    # show only cities with specified prefix
    search_by_prefix = app.request.get("prefix")
    if search_by_prefix:
        cities.filter("name>=", search_by_prefix).filter("name<", search_by_prefix + u"\ufffd")
    # ajax request
    if app.request.is_xhr:
        app.response.headers.add_header("Content-Type", 'application/json')
        return simplejson.dumps(cities or [])
    return app.render('location/cities_list', {'cities': cities})