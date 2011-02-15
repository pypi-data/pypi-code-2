"""
This file is unused right now but the implements a mime type item. Might later be used to
retrieve information about mimetypes, aliases and so on
"""
magic=""
class MagicDetector(object):
    """helper class for storing magic strings"""

    def __init__(self, entry):
        """initialize the magic detector with a magic string from the freedesktop magic db"""
        self.entry = entry

class MimeType(object):
    """a mime type definition with detection capabilities"""

    def __init__(self,
                 mimetype = "image/jpeg",
                 globs = ['*.jpg', '*.jpeg', '*.jpe'],
                 magic = MagicDetector(magic),
                 name="JPEG Image",
                 names={},
                 aliases = ["image/pjpeg"],
                 canonical = None):
    	"""initialize this mimetype with the ``mimetype``, e.g. ``image/jpeg``.
    	a list of glob patterns for matching against the filename in ``globs``, an optional 
    	detector for file contents in ``magic``, a flag if it's binary data in ``is_binary``
    	and the english name in ``name``, e.g. "JPEG Image". All international names are stored
    	in ``names`` as a dict, e.g. ``{'de': 'JPEG-Bild'}``.

    	You can additionally give alias names in ``aliases``. Note that aliases only are stored
    	in the canonical/main mimetypes, not in the aliased types. The canonical form is references
    	in ``canonical``.

    	"""

    	self.name = name
    	self.globs = globs
    	self.magic = magic
    	self.major, self.minor = name.split("/")
    	self.name = name
    	self.names = names

    	self.aliases = aliases
    	self.canonical = canonical





