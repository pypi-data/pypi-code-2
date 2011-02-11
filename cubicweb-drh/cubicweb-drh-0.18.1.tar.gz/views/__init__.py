"""drh web ui"""

from cubicweb.web import uicfg

uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Person', 'concerned_by', '*'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('*', 'todo_by', 'Person'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Application', 'for_person', 'Person'), True)
uicfg.actionbox_appearsin_addmenu.tag_subject_of(('School', 'filed_under', 'Folder'), False)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Application', 'for_person', 'Person'), True)
uicfg.autoform_section.tag_subject_of(('School', 'use_email', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('School', 'phone', '*'), 'main', 'attributes')
uicfg.primaryview_section.tag_subject_of(('Person', 'concerned_by', '*'), 'hidden')
uicfg.primaryview_section.tag_object_of(('*', 'topic', 'Application'), 'hidden')
uicfg.autoform_section.tag_subject_of(('Application', 'for_person', 'Person'), 'main', 'attributes')
