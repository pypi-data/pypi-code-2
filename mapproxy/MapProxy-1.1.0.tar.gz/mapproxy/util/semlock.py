
import ctypes
libc = ctypes.CDLL('libc.dylib')
O_CREAT = 0x0200 # create if nonexistant

libc.sem_unlink.args = [ctypes.c_char_p]

libc.sem_open.args = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
libc.sem_open.restype = ctypes.c_void_p

libc.sem_trywait.args = [ctypes.c_void_p]
libc.sem_trywait.restype = ctypes.c_int

libc.sem_post.args = [ctypes.c_void_p]
libc.sem_post.restype = ctypes.c_int



if __name__ == '__main__':
    libc.sem_unlink('testsem1')
    res = libc.sem_open('testsem1', O_CREAT, 0600, 2)
    print libc.sem_trywait(res)
    print libc.sem_trywait(res)
    print libc.sem_trywait(res)
    # TODO remove breakpoint
    import ipdb; ipdb.set_trace()
