#!/usr/bin/env python2
# -*- coding: utf-8 -*-

menu_cmd = (
    ('Capture Entire Screen', 'scru -s -noup'),
    ('Capture window or Area', 'scrot -sw -noup'),
    ('Capture Entire Screen &amp; Upload', 'scru -sn -q80'),
    ('Capture window or Area &amp; Upload', 'scru -snw -q80'))

print('<openbox_pipe_menu>')
for label, command in menu_cmd:
    print('  <item label="%s">' % label)
    print('    <action name="Execute">')
    print('      <execute>')
    print('        %s' % command)
    print('      </execute>')
    print('    </action>')
    print('  </item>')
print('</openbox_pipe_menu>')


