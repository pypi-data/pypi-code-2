from causal import get_version

def causal_version(context):
    """Add the current version to the context, handy for adding to a meta tag
    for debug.
    """
    return {'CAUSAL_VERSION': get_version()}
