from limoncello import *
from rum import app

def get_dialect_name():

    try:
        return app.repositoryfactory.session_factory.bind.dialect.name
    except AttributeError:
        return "GENERIC"