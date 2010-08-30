import uuid


def createAtomicDefinition(contextManager, name=None):

    builder = contextManager.pomsetBuilder()
    executableObject = builder.createExecutableObject([], staticArgs=[])

    id = uuid.uuid4().hex

    # autogenerate the name of the definition
    if name is None:
        name = '_'.join(['definition', id[:3]])

    definitionContext = builder.createNewAtomicPomset(
        name=name, executableObject=executableObject)
    definition = definitionContext.pomset()
    definition.id(id)

    contextManager.transientLibrary().addPomsetContext(definitionContext)

    return definitionContext

