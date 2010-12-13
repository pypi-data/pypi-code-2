"""Docstring tests is borrowed from django tests for sessions backend"""

__test__ = {"doctest": """
>>> from django.conf import settings
>>> from hs_sessions.handlersocket import SessionStore as HandlerSocketSession
>>> from django.contrib.sessions.models import Session

>>> db_session = HandlerSocketSession()
>>> db_session.modified
False
>>> db_session.get('cat')
>>> db_session['cat'] = "dog"
>>> db_session.modified
True
>>> db_session.pop('cat')
'dog'
>>> db_session.pop('some key', 'does not exist')
'does not exist'
>>> db_session.save()
>>> db_session.exists(db_session.session_key)
True
>>> db_session.delete(db_session.session_key)
>>> db_session.exists(db_session.session_key)
False

>>> db_session['foo'] = 'bar'
>>> db_session.save()
>>> db_session.exists(db_session.session_key)
True
>>> prev_key = db_session.session_key
>>> db_session.flush()
>>> db_session.exists(prev_key)
False
>>> db_session.session_key == prev_key
False
>>> db_session.modified, db_session.accessed
(True, True)
>>> db_session['a'], db_session['b'] = 'c', 'd'
>>> db_session.save()
>>> prev_key = db_session.session_key
>>> prev_data = db_session.items()
>>> db_session.cycle_key()
>>> db_session.session_key == prev_key
False
>>> db_session.items() == prev_data
True

# Submitting an invalid session key (either by guessing, or if the db has
# removed the key) results in a new key being generated.
>>> Session.objects.filter(pk=db_session.session_key).delete()
>>> db_session = HandlerSocketSession(db_session.session_key)
>>> db_session.save()
>>> HandlerSocketSession('1').get('cat')
"""}

