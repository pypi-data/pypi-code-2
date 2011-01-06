#!/usr/bin/python
import math

def find_terminal_size():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])

def find_terminal_width():
    return find_terminal_size()[0]

def find_terminal_height():
    return find_terminal_size()[1]

def build_progress(numerator, denominator, width=None):
    if width == None:
        width = find_terminal_width()
    width = width - 12
    if width <= 1:
        return '%7s' % ('%%%.2f' % (100.0 * percent))

    percent  = float(numerator) / float(denominator)
    complete = int(math.floor(percent*width))
    return '[ ' + '#'*complete + '.'*(width-complete) + ' ] %7s' % ('%%%.2f' % (100.0 * percent))

if __name__ == '__main__':
    #print getTerminalSize()
    print build_progress(26,100) + '\r',
    print build_progress(99,100) + '\r',
    print build_progress(100,100) + '\r',
    print ''