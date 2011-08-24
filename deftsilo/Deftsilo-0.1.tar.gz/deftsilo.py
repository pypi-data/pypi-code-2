#!/usr/bin/env python

# Copyright (c) 2011, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of deftsilo nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import print_function


import getopt
import hashlib
import os
import os.path
import shlex
import subprocess
import tarfile
import tempfile


def pathscheme_base(path):
    return '.' + os.path.basename(path)


def get_sha1s_for(path):
    path = os.path.normpath(path)
    pipe = subprocess.Popen(["git", "rev-list", "--objects", "--all"],
            shell=False, stdout=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    ret = []
    for line in stdout.split('\n'):
        if ' ' not in line:
            continue
        sha1, fname = line.split(' ', 1)
        if os.path.normpath(fname) == path:
            shapipe = subprocess.Popen(["git", "cat-file", "blob", sha1],
                    shell=False, stdout=subprocess.PIPE)
            stdout, stderr = shapipe.communicate()
            ret.append(hashlib.sha1(stdout).hexdigest())
    return ret


def get_data_for(path):
    path = os.path.normpath(path)
    pipe = subprocess.Popen(["git", "rev-list", "--objects", "--all"],
            shell=False, stdout=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    ret = []
    for line in stdout.split('\n'):
        if ' ' not in line:
            continue
        sha1, fname = line.split(' ', 1)
        if os.path.normpath(fname) == path:
            shapipe = subprocess.Popen(["git", "cat-file", "blob", sha1],
                    shell=False, stdout=subprocess.PIPE)
            stdout, stderr = shapipe.communicate()
            if shapipe.returncode != 0:
                return None
            return stdout
    return None


def shell_escape(path): return path


def generate_copy(src, dst, sha1s):
    src = shell_escape(src)
    dst = shell_escape(dst)
    ret = ''
    outer_prefix = ''
    copy_line = 'cp "{0}" "${{DESTDIR}}/{1}"'.format(src, dst)
    if sha1s:
        ret += 'if [ -f "${{DESTDIR}}/{0}" ]; then\n'.format(dst)
        outer_prefix = 'el'
        inner_prefix = ''
        for sha1 in sha1s:
            ret += '    {0}if [ `hash ${{DESTDIR}}/{1}` = {2} ]; then\n'.format(inner_prefix, dst, sha1)
            ret += '        {0}\n'.format(copy_line)
            inner_prefix = 'el'
        ret += '    else\n'
        ret += '        echo \'Cannot copy "{0}" to "\'${{DESTDIR}}/{1}\'" as there are unsaved changes.\'\n'.format(src, dst)
        ret += '    fi\n'
    ret += '{0}if [ ! -e "${{DESTDIR}}/{1}" ]; then\n'.format(outer_prefix, dst)
    ret += '    {0}\n'.format(copy_line)
    ret += 'else\n'
    ret += '    echo \'Cannot copy "{0}" to "\'${{DESTDIR}}/{1}\'" because the target exists.\'\n'.format(src, dst)
    ret += 'fi\n'
    return ret;


def generate_link(src, dst):
    src = shell_escape(src)
    dst = shell_escape(dst)
    link_line = 'ln -s `realpath "{0}"` "${{DESTDIR}}/{1}"'.format(src, dst)
    ret  = 'if [ -L "${{DESTDIR}}/{0}" ] && \n'.format(dst)
    ret += '   [ `realpath {0}` != `realpath "${{DESTDIR}}"/{1}` ]; then\n'.format(src, dst)
    ret += '    echo \'Cannot link "\'${{DESTDIR}}/{1}\'" -> "{0}" because the link points elsewhere.\'\n'.format(src, dst)
    ret += 'elif [ -L "${{DESTDIR}}/{0}" ]; then\n'.format(dst)
    ret += 'elif [ -e "${{DESTDIR}}/{0}" ]; then\n'.format(dst)
    ret += '    echo \'Cannot link "\'${{DESTDIR}}/{1}\'" -> "{0}" because the link exists.\'\n'.format(src, dst)
    ret += 'else\n'
    ret += '    {0}\n'.format(link_line)
    ret += 'fi\n'
    return ret


def parse_copy(args):
    opts, args = getopt.getopt(args, '', [])
    if len(args) not in (1, 2):
        raise RuntimeError("Copy command should take 1 or 2 arguments");
    if len(args) == 2:
        target = args[1]
    else:
        target = pathscheme_base(args[0])
    sha1s = get_sha1s_for(args[0])
    return generate_copy(args[0], target, sha1s), [args[0]]


def parse_link(args):
    opts, args = getopt.getopt(args, '', [])
    if len(args) not in (1, 2):
        raise RuntimeError("Link command should take 1 or 2 arguments");
    if len(args) == 2:
        target = args[1]
    else:
        target = pathscheme_base(args[0])
    return generate_link(args[0], target), [args[0]]


def parse_mkdir(args):
    opts, args = getopt.getopt(args, '', [])
    if len(args) not in (1,):
        raise RuntimeError("Mkdir command should take 1 argument");
    return 'mkdir "${{DESTDIR}}/{0}"\n'.format(args[0]), []


def parse_line(lineno, args):
    if args[0] == 'copy':
        return parse_copy(args[1:])
    elif args[0] == 'link':
        return parse_link(args[1:])
    elif args[0] == 'mkdir':
        return parse_mkdir(args[1:])
    else:
        errstr = 'Unknown command "{0}" on line {1}'
        raise RuntimeError(errstr.format(args[0], lineno))


def parse(source):
    scripts = []
    allfiles = []
    command = ''
    count = 1
    for i, line in enumerate(source.split('\n')):
        if line.endswith('\\'):
            command += line[:-1] + ' '
        elif line:
            command += line
            script, files = parse_line(count, shlex.split(command, posix=True))
            scripts.append(script)
            allfiles += files
            command = ''
            count = i + 2
    ret  = 'hash ()\n'
    ret += '{\n'
    ret += "    shasum $1 | awk '{print $1}'\n"
    ret += '}\n\n'
    ret += '\n'.join([script for script in scripts if script])
    return ret, list(sorted(set(allfiles)))


def main(args):
    opts, args = getopt.getopt(args, '', [])
    if len(args) != 2:
        raise RuntimeError("Usage:  deftsilo <command> <source>")
    with open(args[1]) as fin:
        dirname = os.path.dirname(args[1])
        if dirname:
            os.chdir(dirname)
        data = fin.read()
        script, files = parse(data)
        if args[0] == 'generate':
            tar = tarfile.open(args[1] + '.tar.gz', 'w:gz')
            for filename in files:
                with tempfile.NamedTemporaryFile() as tmp:
                    data = get_data_for(filename)
                    if data is None:
                        raise RuntimeError('Could not read "{0}" from git'.format(filename))
                    tmp.write(data)
                    tmp.flush()
                    tar.add(tmp.name, os.path.join(args[1], filename))
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(script)
                tmp.flush()
                tar.add(tmp.name, os.path.join(args[1], 'run.sh'))
            tar.close()
        elif args[0] == 'run':
            pipe = subprocess.Popen(["sh"], shell=False, stdin=subprocess.PIPE)
            pipe.communicate(script)
            if pipe.returncode != 0:
                raise RuntimeError("Shell exited non-zero")
        elif args[0] == 'debug':
            print(script)
        else:
            raise RuntimeError('Unknown command "{0}"'.format(args[0]))
    return 0

if __name__ == '__main__':
    import sys
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
