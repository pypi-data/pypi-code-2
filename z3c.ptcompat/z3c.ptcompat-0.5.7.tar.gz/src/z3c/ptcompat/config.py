import os
import logging
import z3c.ptcompat
import weakref

REGISTRY = weakref.WeakKeyDictionary()

PREFER_Z3C_PT = os.environ.get("PREFER_Z3C_PT", 'false').lower() in \
                ('y', 'yes', 't', 'true', 'on', '1')

if PREFER_Z3C_PT:
    try:
        import z3c.pt
    except ImportError:
        logging.getLogger('z3c.ptcompat').warn(
            "Unable to import ``z3c.pt``.")
        PREFER_Z3C_PT = False

def enable():
    global PREFER_Z3C_PT
    PREFER_Z3C_PT = True
    reload(z3c.ptcompat)

    for inst, (args, kwargs) in REGISTRY.items():
        migrate(inst, args, kwargs)

def disable():
    global PREFER_Z3C_PT
    PREFER_Z3C_PT = False
    reload(z3c.ptcompat)

    for inst, (args, kwargs) in REGISTRY.items():
        migrate(inst, args, kwargs)

def migrate(inst, args, kwargs):
    cls = inst.__class__
    new_cls = getattr(z3c.ptcompat, cls.__name__)
    inst.__class__ = new_cls
    inst.__dict__.clear()
    try:
        inst.__init__(*args, **kwargs)
    except (OSError, ValueError):
        # remove broken templates from registry
        REGISTRY.pop(inst, None)
