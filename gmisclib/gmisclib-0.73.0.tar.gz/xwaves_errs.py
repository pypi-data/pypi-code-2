"""Errors for reading label (typically speech transcription) files.
"""

class Error(Exception):
	def __init__(self, *x):
		Exception.__init__(self, *x)

class NoSuchFileError(IOError, Error):
	def __init__(self, *x):
		IOError.__init__(self, *x)
		Error.__init__(self, *x)

class BadFileFormatError(Error):
	def __init__(self, *x):
		Error.__init__(self, *x)

class DataError(Error):
	def __init__(self, *x):
		Error.__init__(self, *x)

# class DataOutOfOrderError(DataError):
	# def __init__(self, *s):
		# Error.__init__(self, *s)

class DataOutOfOrderError(DataError):
	def __init__(self, *s):
		DataError.__init__(self, *s)
