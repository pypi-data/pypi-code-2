import os, sys
import subprocess
import argparse

def split_all(path):
    items = []
    split = (os.path.normpath(path), '')
    while split[0]:
        split = os.path.split(split[0])
        if (split[1]):
            items.insert(0, split[1])
    return items

def split_base(path, start):
    path, start = map(split_all, (path, start))
    if not start:
        raise ValueError("start path most not be empty")
    for idx in range(len(path)):
        if path[idx] == start[0]:
            if path[idx:idx+len(start)] == start:
                return os.path.join(*path[:idx+len(start)]), os.path.join(*path[idx+len(start):])
    return None

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("merged",
                        help="File with all merged changes (and conflicts). All changes occur in this file")
    parser.add_argument("local",
                        help="Current branch version")
    parser.add_argument("base",
                        help="Common ancestor")
    parser.add_argument("remote",
                        help="Version to be merged")
    opts = parser.parse_args(args)
    merged = opts.merged

    split = split_base(merged, "modules/scope")
    if not split:
        print >> sys.stderr, "Could not locate modules/scope in path\nThis tool can only work within the scope directory"
        sys.exit(1)
    scope_path, file_path = split
    args = ["hob", "cpp", "-r", file_path]
    print "Executing: %s" % (" ".join(args))
    subprocess.check_call(args, cwd=scope_path)

if __name__ == "__main__":
    main()
