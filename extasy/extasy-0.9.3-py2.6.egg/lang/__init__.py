import extasy
import os

_loaded = False
lang = {}


def _load():
    global _loaded
    global lang
    if not _loaded:
        langModule = __import__( 'extasy.lang.%s' % extasy.settings.get( 'language', 'en-us' ), fromlist = [ 'lang' ] )
        lang = langModule.lang
        _loaded = True

    
def get( message ):
    global lang
    
    _load()
        
    if message in lang:
        return lang[ message ]
        
    elif message.capitalize() in lang:
        return lang[ message.capitalize() ]
        
    elif len(message) > 1:
        uncapitalized_message = message[0].lower() + message[1:]
        if uncapitalized_message in lang:
            return lang[ uncapitalized_message ]
        
    return message
    
def has_key( message ):
    global lang

    _load()

    if message in lang:
        return true

    elif message.capitalize() in lang:
        return true

    elif len(message) > 1:
        uncapitalized_message = message[0].lower() + message[1:]
        if uncapitalized_message in lang:
            return true

    return false