#!/usr/bin/python -tt

import urllib2

def resolve_filename( location ):
	return open( location, 'r' ).read( )

def resolve_url( location ):
	return urllib2.urlopen( location ).read( )
