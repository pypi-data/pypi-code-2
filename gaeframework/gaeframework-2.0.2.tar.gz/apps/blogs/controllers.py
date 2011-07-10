'''
Blogs - multiple blogs in one application
''' 
from user import login_required
from gae.shortcuts import get_object_or_404
from blog.models import Blog, Entity
from blog.forms import BlogCreateForm, BlogEditForm,\
                            EntityCreateForm, EntityEditForm
from gae.pages import Pages

''' operations with blogs '''

def blogs_list(app):
    blogs = Blog.all().order('-created')
    # show not published blogs
    if app.request.GET.get("show") == "unpublished" and app.user:
        # show all blogs
        blogs.filter('active', False)
        # show only user blogs
        if not app.user.is_admin:
            blogs.filter('author', app.user)
    # show only active blogs
    else:
        blogs.filter('active', True)
    # render page
    return app.render('blog/blogs_list', {
                      'blogs': Pages(blogs, 20, "blogs_page"),
                      })

@login_required()
def blog_create(app):
    if app.request.POST:
        form = BlogCreateForm(data=app.request.POST)
        # filled form
        if form.is_valid():
            form.save()
            return app.redirect("go back")
    else:
        # empty form
        form = BlogCreateForm()
    # render page
    return app.render('blog/blog_create', {'form': form})

@login_required()
def blog_edit(app, blog):
    blog_obj = Blog.get_by_key_name(blog)
    # item not found
    if blog_obj is None:
        return app.error(404)
    if app.request.POST:
        # filled form
        form = BlogEditForm(data=app.request.POST, instance=blog_obj)
        if form.is_valid():
            form.save()
            return app.redirect("go back")
    else:
        # empty form with initial data
        form = BlogEditForm(instance=blog_obj)
    # render page
    return app.render('blog/blog_edit', {'form': form})

@login_required()
def blog_delete(app, blog):
    blog_obj = Blog.get_by_key_name(blog)
    # item not found
    if blog_obj is None:
        return app.error(404)
    # delete blog
    blog_obj.delete()
    return app.redirect("go back")

''' operations with blog entities '''

def entities_list(app, blog=None, tags=None):
    blog_obj = blog and Blog.get_by_key_name(blog)
    entities = Entity.all().order('-changed')
    if blog_obj:
        entities.filter('blog', blog_obj)
    if tags:
        entities.filter('tags IN', tags.strip().split(','))
    # show not published entities
    if app.request.GET.get("show") == "unpublished" and app.user:
        # show all entities
        entities.filter('active', False)
        # show only user entities
        if not app.user.is_admin:
            entities.filter('author', app.user)
    # show only active blogs
    else:
        entities.filter('active', True)
    # render page
    return app.render('blog/entities_list', {
                      'blog': blog_obj,
                      'entities': Pages(entities, 20, "entities_page"),
                      })

def entity_details(app, blog, entity):
    blog_obj = get_object_or_404(Blog, slug=blog)
    entity_obj = get_object_or_404(Entity, slug="%s/%s" % (blog_obj.key().name(), entity))
    # render page
    return app.render('blog/entity_details', {
                      'blog': blog_obj,
                      'entity': entity_obj})

@login_required()
def entity_create(app, blog):
    blog_obj = get_object_or_404(Blog, slug=blog)
    if app.request.POST:
        form = EntityCreateForm(data=app.request.POST, initial={'blog': blog_obj})
        # filled form
        if form.is_valid():
            form.save()
            return app.redirect("go back")
    else:
        # empty form
        form = EntityCreateForm()
    # render page
    return app.render('blog/entity_create', {'form': form})

@login_required()
def entity_edit(app, blog, entity):
    blog_obj = get_object_or_404(Blog, slug=blog)
    entity_obj = get_object_or_404(Entity, slug="%s/%s" % (blog_obj.key().name(), entity))
    if app.request.POST:
        # filled form
        form = EntityEditForm(data=app.request.POST, instance=entity_obj)
        if form.is_valid():
            form.save()
            return app.redirect("go back")
    else:
        # empty form with initial data
        form = EntityEditForm(instance=entity_obj)
    # render page
    return app.render('blog/entity_edit', {'form': form})

@login_required()
def entity_delete(app, blog, entity):
    blog_obj = get_object_or_404(Blog, slug=blog)
    entity_obj = get_object_or_404(Entity, slug="%s/%s" % (blog_obj.key().name(), entity))
    # delete blog entity
    entity_obj.delete()
    return app.redirect("go back")