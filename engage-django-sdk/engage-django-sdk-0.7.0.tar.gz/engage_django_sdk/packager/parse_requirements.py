import re
def parse_requirements(fp):
    requirements = []
    dependencies = []
    for line in fp.read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-r\s+', line):
            dependencies.append(re.sub(r'\s*-r\s+', '', line))
        elif re.match(r'\s*-f\s+', line):
            requirements.append(re.sub(r'\s*-f\s+[^\s]*\s+([^\>\<\=]*)[\>|\>\=|\=\=](.*)$', r'\1', line))
        elif re.match(r'\s*--find-links\s*', line):
            requirements.append(re.sub(r'\s*--find-links\s+[^\s]*\s+([^\>\<\=]*)[\>|\>\=|\=\=](.*)$', r'\1', line))
        elif re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'(.*)[\>|\>\=|\=\=](.*)$', line):
            requirements.append(re.sub(r'([^\>\=\<]*)[\>|\>\=|\=\=](.*)$', r'\1', line))
        elif re.match(r'\s*index-url\s*', line):
            print 'Warning: --index-url not supported yet.'
            pass
        else:
            requirements.append(line)
    return (requirements, dependencies)

def parse_dependency_links(fp):
    dependency_links = []
    for line in fp.read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    return dependency_links

def parse(fname):
    packages = []
    fset = set()
    files = [fname]
    while (files):
        f = files.pop()
        if f in fset:
            print 'Warning: circular dependency in requirements.txt file: %s' % f
            break
        fset.add(f)
        try:
            fp = open(f, 'r')
        except IOError:
            print 'Warning: requirements file %s not found for reading' % f
            break
        (reqs, deps) = parse_requirements(fp)
        fp.close()
        packages = packages + reqs
        files = files + deps
    return packages

if __name__ == '__main__':
    packages = parse('requirements.txt') 
    print packages
