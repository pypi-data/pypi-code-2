from zope.pagetemplate.pagetemplatefile import PageTemplateFile

class JSTemplateFile(PageTemplateFile):
    """
    Zope wrapper for filesystem JavaScript Template
    """
    
    def _read_file(self):
        __traceback_info__ = self.filename
        f = open(self.filename, "rb")
        try:
            text = f.read()
        except:
            f.close()
            raise
        type_ = "text/javascript"
        f.close()
        return text, type_
