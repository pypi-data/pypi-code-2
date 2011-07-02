'''
Blogs - multiple blogs in one application
''' 
from gae.pages import Pages
from gae.shortcuts import get_object_or_404
from apps.user import login_required
from apps.blog.models import Entity
from apps.blog.forms import EntityCreateForm, EntityEditForm

def entries_list(app, tags=None):
    entries = Entity.all().order('-changed')
    if tags:
        entries.filter('tags IN', tags.strip().split(','))
    # show not published entries
    if app.request.GET.get("show") == "unpublished" and app.user:
        # show all entries
        entries.filter('active', False)
        # show only user entries
        if not app.user.is_admin:
            entries.filter('author', app.user)
    # show only active entries
    else:
        entries.filter('active', True)
    # render page
    return app.render('blog/entries_list', {
                      'entries': Pages(entries, 10, "entries_page"),
                      })

def entry_details(app, entry):
    entry_obj = get_object_or_404(Entity, slug=entry)
    return app.render('blog/entry_details', {
                      'entry': entry_obj})

@login_required()
def create_entry(app):
    if app.request.POST:
        form = EntityCreateForm(data=app.request.POST)
        # filled form
        if form.is_valid():
            form.save()
            return app.redirect("go back")
    else:
        # empty form
        form = EntityCreateForm()
    # render page
    return app.render('blog/create_entry', {'form': form})

@login_required()
def edit_entry(app, entry):
    entry_obj = get_object_or_404(Entity, slug=entry)
    if app.request.POST:
        # filled form
        form = EntityEditForm(data=app.request.POST, instance=entry_obj)
        if form.is_valid():
            form.save()
            return app.redirect("go back")
    else:
        # empty form with initial data
        tags = ", ".join(entry_obj.tags or [])
        form = EntityEditForm(instance=entry_obj, initial={"tags": tags})
    # render page
    return app.render('blog/edit_entry', {'form': form})

@login_required()
def delete_entry(app, entry):
    entry_obj = get_object_or_404(Entity, slug=entry)
    entry_obj.delete()
    return app.redirect("go back")