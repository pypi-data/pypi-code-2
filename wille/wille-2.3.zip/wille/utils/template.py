"""template - Light-weight template engine

"""

import os

ENCODING_FALLBACK_CHARSET = 'utf-8'

def render(template_filename, vars=dict(), \
		   file_encoding=ENCODING_FALLBACK_CHARSET, template_dir=None):
	"""Simple templatefile renderer, supporting ${xyz} style variables
		
	Returns: rendered template as unicode() object
	"""
	template_filepath = os.path.join(template_dir, template_filename)
	f = open(template_filepath,'r')
	data = unicode( f.read(), file_encoding )
	f.close()
	
	return render_str(data, vars)

def render_str(data, vars=None, vars_encoding=ENCODING_FALLBACK_CHARSET):
	"""Render string template using given set of variables:
		data - Template string
		vars - Dictionary of variables with they content
		vars_encoding - Default encoding for plaintext variables
		                (enforced if template is in unicode format)
	
	Rendering in cases of 0-2 vars:
	
	>>> from template import render_str
	
	>>> render_str('Hello World!')
	'Hello World!'

	>>> render_str('Hello ${world}!', {'world': 'World'})
	'Hello World!'
	
	>>> render_str('${hello} ${world}!', {'hello': 'Hello', 'world': 'World'})
	'Hello World!'

	>>> render_str(u'1234\\u1234\\n').encode('utf-8')
	'1234\\u1234\\n'
	
	# (Note that above we have escaped all backslashes to make code work
	# in doctest)
	
	"""
	
	# Replace varname with vars
	if vars:
		for var in vars:
			original = '${%s}' % var
			replace = '%s' % vars[var]
			
			# If data is unicode and replace is not, convert it to unicode
			if type(data)==unicode and type(original)==str:
				original = unicode(original, vars_encoding)
			if type(data)==unicode and type(replace)==str:
				replace = unicode(replace, vars_encoding)
			
			try:
				data = data.replace(original,replace)
			except UnicodeDecodeError, e:
				raise Exception("UnicodeDecodeError while processing var %s (type(data)=%s, type(replace)=%s" % (var, type(data), type(replace)), e)
	
	return data

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
