import sys
import os
from xml.etree import cElementTree as ET


def main(args=None,orig_cmd_path=None):
    if args is None:
        args = sys.argv

    if len(args) > 1:
        target_dir = args[-1]
        if not os.path.isdir(target_dir):
            raise SystemExit('%s is not a directory' % (target_dir,))
    else:
        target_dir = os.getcwd()

    root = ET.Element('directory', name=target_dir)
    for fn in os.listdir(target_dir):
        stat = os.stat(os.path.join(target_dir, fn))
        f_el = ET.SubElement(root, 'file', mtime=str(stat.st_mtime))
        ET.SubElement(f_el, 'name').text = fn
        ET.SubElement(f_el, 'size').text = str(stat.st_size)
    ET.ElementTree(root).write(sys.stdout, 'utf-8')
    sys.stdout.write('\n')

if __name__ == '__main__':
    main()
