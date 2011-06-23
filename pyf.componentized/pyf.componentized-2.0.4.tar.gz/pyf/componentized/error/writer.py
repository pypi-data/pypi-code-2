class WriterError(Exception):
    pass

class MissingConfigSectionError(WriterError):
    pass

class MissingConfigEntryError(WriterError):
    pass
