'''
Comments - attach comments to any object.
'''
from apps.comment.forms import UserCommentForm
from apps.user import login_required
from gae import db
import re

@login_required()
def create_comment(app):
    """
    Create a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comment/preview.html``, will be rendered.
    """
    data = app.request.POST.copy()
    if data:
        # get object model name
        object_key = db.Key(data['obj'])
        object_type = object_key.kind()
        # get application name
        path = re.findall("[A-Z][^A-Z]*", object_type)[0].lower()
        try:
            # load module with object, attached to comment
            __import__("%s.models" % (path))
        except ImportError:
            raise Exception("Not found object '%s' in application '%s'" % (object_type, path))
        # filled form
        form = UserCommentForm(data=data, initial={"obj": object_key})
        # preview the comment
        if "preview" in data or not form.is_valid():
            return app.render('comments/preview', {
                              "form":     form,
                              "comment":  form.data.get("text", ""),
                              })
        form.save()
    return app.redirect("go back")
