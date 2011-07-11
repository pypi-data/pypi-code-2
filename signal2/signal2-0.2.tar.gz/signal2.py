import ctypes
from ctypes_configure import configure

libc = ctypes.CDLL(None)

class siginfo_t(ctypes.Structure):
    pass # forward reference

class sigval_t(ctypes.Union):
    _fields_ = [
        ('sigval_int', ctypes.c_int),
        ('sigval_ptr', ctypes.c_void_p)
        ]

sa_sigaction_t = ctypes.CFUNCTYPE(None,
                                  ctypes.c_int,
                                  ctypes.POINTER(siginfo_t),
                                  ctypes.c_void_p)

class _CConfigure:
    _compilation_info_ = configure.ExternalCompilationInfo(
        includes = ['signal.h', 'sys/types.h', 'unistd.h'],
        )

    pid_t = configure.SimpleType('pid_t', ctypes.c_int)

    SA_SIGINFO = configure.ConstantInteger('SA_SIGINFO')

    struct_sigaction = configure.Struct('struct sigaction', [
            ('sa_flags', ctypes.c_int),
            ('sa_sigaction', sa_sigaction_t)
            ])

    siginfo_t = configure.Struct('siginfo_t', [
            ('si_signo', ctypes.c_int),
            ('si_value', sigval_t)
            ])

_info = configure.configure(_CConfigure)

pid_t = _info['pid_t']
struct_sigaction = _info['struct_sigaction']
siginfo_t._fields_ = _info['siginfo_t']._fields_
SA_SIGINFO = _info['SA_SIGINFO']

sigaction = libc.sigaction
sigaction.argtypes = [ctypes.c_int,
                      ctypes.POINTER(struct_sigaction),
                      ctypes.POINTER(struct_sigaction)]
sigaction.restype = ctypes.c_int

sigqueue = libc.sigqueue
sigqueue.argtypes = [pid_t, ctypes.c_int, sigval_t]
sigqueue.restype = ctypes.c_int


def install_sigaction(signo, sa_flags, handler):
    """
    Convenience function to install a sigaction() handler
    """
    action = struct_sigaction()
    action.sa_flags = SA_SIGINFO
    action.sa_sigaction = sa_sigaction_t(handler)
    return sigaction(signo, ctypes.pointer(action), None)
