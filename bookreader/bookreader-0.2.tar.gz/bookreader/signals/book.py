from bookreader import harvesting


def load_metadata(sender, instance, **kwargs):
    harvesting.load_metadata(instance)

def load_pages(sender, instance, created, **kwargs):
    harvesting.load_pages(instance)

def load_links(sender, instance, created, **kwargs):
    harvesting.load_links(instance)
