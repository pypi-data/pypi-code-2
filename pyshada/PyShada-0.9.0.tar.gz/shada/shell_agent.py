import comm
import sys, os

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(255)
        pass
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    client = comm.client(cmd, args, os.environ, sys.stdin, sys.stdout)
    client.connect()
    client.handle()
    pass
