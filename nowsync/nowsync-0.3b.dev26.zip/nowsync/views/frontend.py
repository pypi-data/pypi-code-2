from flask import Module
from flaskext.genshi import render_response

frontend = Module(__name__)

@frontend.route('/')
def index():
    return render_response('index.html')
