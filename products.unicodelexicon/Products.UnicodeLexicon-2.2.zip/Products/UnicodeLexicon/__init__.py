"""UnicodeLexicon initialization module.
"""

def getElementGroups(self):
    from pipelinefactory import element_factory
    return element_factory.getFactoryGroups()


def getElementNames(self, group):
    from pipelinefactory import element_factory
    return element_factory.getFactoryNames(group)


def initialize(context):
    """Initialize the UnicodeLexicon product."""

    from lexicon import UnicodeLexicon
    from lexicon import manage_addLexiconForm
    from lexicon import manage_addLexicon

    context.registerClass(
        UnicodeLexicon,
        permission='Add Vocabularies',
        constructors=(manage_addLexiconForm,
                      manage_addLexicon,
                      getElementGroups,
                      getElementNames),
        icon='www/lexicon.gif'
    )

