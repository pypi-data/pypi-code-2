from gae.tools import Pagination
from gae.shortcuts import get_object_or_404
from gae.decorators import render


@render()
def index(request):
    return "[app_name]/index.html"
