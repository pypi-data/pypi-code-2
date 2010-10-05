# postcreate script. You could setup a workflow here for example
wf = add_workflow('task workflow', 'Task')
todo = wf.add_state(_('todo'), initial=True)
done = wf.add_state(_('done'))
wf.add_transition(_('done'), todo, done)

commit()
