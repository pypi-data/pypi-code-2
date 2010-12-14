
def check_tube(repository, tube, variant=None):
    # Trying to see if there is a newer version on the repo...
    repository.check_item(tube)
    
    if variant is not None:
        for layer in tube.get_ordered_layers(variant=variant):
            repository.check_item(layer)

def check_descriptor(repository, descriptor):
    repository.check_item(descriptor)

def check_dispatch(repository, dispatch, variant=None):
    check_tube(repository, dispatch.tube, variant=variant)
    check_descriptor(repository, dispatch.descriptor)