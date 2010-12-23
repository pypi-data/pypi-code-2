# -*- coding: utf-8 -*-
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from common.decorators import render_to
from common.decorators import ajax
from common.forms import build_form

from green_comments.models import Comment
from green_comments.forms import CommentForm

@login_required
def comment_create(request, ct_pk, object_id):
    ct = get_object_or_404(ContentType, pk=ct_pk)
    try:
        object = ct.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404()
    return comment_create_logic(request, object)


@login_required
def comment_reply(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    return comment_create_logic(request, comment.content_object, comment)


@render_to('green_comments/comment_create.html')
def comment_create_logic(request, object, parent=None):
    instance = Comment(content_object=object, user=request.user, parent=parent)
    form = build_form(CommentForm, request, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, u'Комментарий успшено отправлен')
        return redirect(object)
    return {'form': form,
            'object': object,
            'parent': parent,
            }
