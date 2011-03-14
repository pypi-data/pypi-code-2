import os, sys

def main():
    if hasattr(os, 'getuid') and os.getuid() == 0:
        print >> sys.stderr, "Okay."
    else:
        print >> sys.stderr, "What? Make it yourself."

if __name__ == '__main__':
    main()
