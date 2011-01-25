major = '0.2'
minor = ''
tag = 'rc1'
revision = '3'
version = major

if minor:
    version += '.' + minor
if tag:
    version += tag
if revision:
    version += '-r' + revision

