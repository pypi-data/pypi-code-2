'''
Administration interface.
'''
from comment.forms import CommentAdminForm, CommentInlineAdminForm

class Comment():
    name = "Comments list"
    forms = (CommentAdminForm, # create
             CommentAdminForm, # edit
             CommentInlineAdminForm) # edit multiple records