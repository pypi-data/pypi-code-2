#!/usr/bin/env python

from subprocess import Popen, PIPE
import re

RELEASE_BRANCH_PATTERN = re.compile("^release_(.*)")
VERSION_REGEX = "\d\.\d\.\d"

def next_rev(major, minor, previous):
    if previous is None:
        return "%d.%d.%d" % (major, minor, 0)

    return "%d.%d.%d" % (major, minor, previous+1)

HGLATEST_TAG_PATTERN = re.compile("^previous tag:\sv(%s)\s.*" % VERSION_REGEX)

def parse_hglatest(s):
    "previous tag: v0.3.0 @94 (-1 [release_0.3])"
    return map(int, HGLATEST_TAG_PATTERN.match(s).group(1).strip().split("."))

def latest_rev(major, minor):
    """
    :rtype: :int: revision
    """
    p = Popen("hg nearest --regexp '^v%s$'" % VERSION_REGEX, shell=True, stdout=PIPE)
    out = p.communicate()[0].strip()
    if not out:
        # no latest rev
        return None
    # FIX: consider the real output of hg nearest, e.g: previous tag: v0.3.0 @94 (-1 [release_0.3])
    tag_major, tag_minor, tag_rev = parse_hglatest(out)
    if tag_major != major or tag_minor != minor:
        raise ValueError, "Wrong tagged version for this branch!"
    return tag_rev

def get_major_minor():
    """
    :rtype: :tuple:`major, minor`
    """\

    p = Popen("hg branch", shell=True, stdout=PIPE)
    out = p.communicate()[0].strip()
    match = RELEASE_BRANCH_PATTERN.match(out)
    if not match:
        raise ValueError, "We're not on a release branch!"
    major_minor = match.group(1)
    return map(int, major_minor.split("."))

def main():
    major, minor = get_major_minor()
    print next_rev(major, minor, latest_rev(major, minor))

if __name__ == "__main__":
    main()




