patched_collage_types = lambda: ('CollageRow', 'CollageColumn', 'CollageAlias')

def apply_collage_types_patch(scope, original, replacement):
    setattr(scope, original, replacement())
    return

def enabledType(self, portal_type):
    if portal_type == 'Collage':
        return True
    else:
        return self._old_enabledType(portal_type)

def enabledAlias(self, portal_type):
    if portal_type == 'Collage':
        return True
    else:
        return self._old_enabledAlias(portal_type)
