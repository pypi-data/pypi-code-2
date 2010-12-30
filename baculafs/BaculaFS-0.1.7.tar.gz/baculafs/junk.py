import commands
baculafs_mount_points = [tokens[2] for tokens in
                         [line.split() for line in commands.getoutput('mount -v').split('\n')]
                         if tokens[4].endswith('baculafs')]
if self.fuse_args.mountpoint in baculafs_mount_points :
    raise RuntimeError, 'mountpoint already in use by BaculaFS'
