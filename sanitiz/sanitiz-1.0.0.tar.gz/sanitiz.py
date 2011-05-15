"""This is the 'sanitiz.py' module provides the function sanitize, which goes through a list,
such as a list of times, and replaces the colons and hyphens with periods"""

def sanitize(time_string):
    if '-' in time_string:
        splitter='-'
    elif ':' in time_string:
        splitter=':'
    else:
        return(time_string)
    (min,sec)=time_string.split(splitter)
    return(min + '.' + sec)
