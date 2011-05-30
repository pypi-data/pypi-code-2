# -*- encoding: utf-8 -*-

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import simplejson as json

from ProcImap.ImapMailbox import ImapMailbox
from ProcImap.ImapMessage import maildirflags_from_imap_message

from .forms import MigrationForm
from .models import Migration, Label
from .utils.gmail2gmail import CaptchaError, ServerError, build_migration_service, get_server
from .utils.imaputf7 import imapUTF7Decode

import datetime
import pytils

@csrf_exempt
def index(request):
    if request.method == 'POST':
        form = MigrationForm(request.POST)
        if form.is_valid():
            migration = form.save(commit=False)
            migration.current_since = migration.since
            migration.save()
            return redirect('migrate_mail.migrate', migration=migration.id)
    else:
        form = MigrationForm()
    migrations = Migration.objects.exclude(admin_password='')
    return render_to_response("index.html", {
        'migrations': migrations,
        'form': form,
    })

def migrate(request, migration):
    migration = get_object_or_404(Migration, pk=migration)
    return render_to_response("migration.html", {
        'migration': migration,
    })

def migrate_delete(request, migration):
    migration = get_object_or_404(Migration, pk=migration)
    migration.delete()
    return redirect('migrate_mail.index')

def migrate_results(request, migration):
    migration = get_object_or_404(Migration, pk=migration)
    # remove labels, you aint gonna need them in future
    migration.labels.all().delete()
    # clear all sensitive data from db
    migration.admin_password = ''
    migration.from_password = ''
    migration.auth_token = ''
    migration.save()
    return render_to_response("migration_results.html", {
        'migration': migration,
    })

def migrate_process(request, migration):

    def _sanitize_label(label):
        if label.startswith('&'):
            try:
                label = imapUTF7Decode(label)
            except:
                pass
        label = label.replace('[Gmail]/', '').replace(' ', '_')
        try:
            label = pytils.translit.translify(unicode(label))
        except:
            pass
        return label

    migration = get_object_or_404(Migration, pk=migration)
    from_name = migration.from_email.split('@')[0]
    sane_label = ''
    uid = None

    try:
        migration_service = build_migration_service(migration.domain, migration.admin_username, migration.admin_password, 
            auth_token=migration.auth_token)
    except CaptchaError, e:
        return HttpResponse(e)
    migration.auth_token = migration_service.GetClientLoginToken()
    migration.save()

    try:
        server = get_server(migration.from_email, migration.from_password)
    except ServerError, e:
        return HttpResponse(e)
    
    if migration.labels_processed:
        # get all-mail label, it contains everything we need
        mailbox = ImapMailbox((server, '[Gmail]/All Mail'))
        # fetch messages day by day
        total_post_size = 0
        for uid in mailbox.search('UNDELETED SINCE %s BEFORE %s' % (
            migration.current_since.strftime("%d-%b-%Y"), 
            (migration.current_since + datetime.timedelta(days=1)).strftime("%d-%b-%Y")
        )):
            if uid <= migration.last_uid:
                continue
            message = mailbox[uid]
            # add old flags and date as custom headers
            message.add_header("X-ProcImap-Imapflags", message.flagstring())
            message.add_header("X-ProcImap-ImapInternalDate", message.internaldatestring())
            # compute new flags
            flags = []
            for flag in message.get_imapflags():
                if flag == '\\Deleted':
                    continue
                if flag == '\\Draft':
                    flags.append('IS_DRAFT')
                if flag == '\\Flagged':
                    flags.append('IS_STARRED')
            # fetch message labels
            labels = [label.label for label in Label.objects.filter(migration=migration, uid=uid)]
            if not labels:
                labels = ["Archived"]
            # add top-level label to labels
            labels = ["%s/%s" % (from_name.lower(), label) for label in labels]
            message_body = message.as_string()
            total_post_size += len(message_body)
            migration_service.AddMailEntry(
                mail_message=message_body,
                mail_item_properties=flags,
                mail_labels=labels)
            # 5 megabytes per one import is a safe bet
            if total_post_size > 5 * 1024 * 1024:
                # ugly hack to stay in the same day
                migration.current_since = migration.current_since - datetime.timedelta(days=1)
                break
        
        mailbox.close()

        # do the import itself
        migration.messages_cnt += migration_service.ImportMultipleMails(user_name=migration.to_username, threads_per_batch=5)
        if uid: migration.last_uid = uid

        # go to next date
        migration.current_since = migration.current_since + datetime.timedelta(days=1)
        migration.save()

        if migration.current_since > datetime.date.today():
            return HttpResponse("FINISHED")

    else:
        # process labels
        # gmail doesn't give us sent mail label, so be it
        labels = ['[Gmail]/Sent Mail'] + server.list()
        # filter useless labels out
        labels = [label for label in labels 
            if label not in ['[Gmail]/Drafts', '[Gmail]/Trash', '[Gmail]/Spam', '[Gmail]/All Mail', '[Gmail]/Starred']]
        # cut processed labels
        if migration.current_label:
            labels = labels[labels.index(migration.current_label):]
        # process label or switch to next
        for i in range(len(labels)):
            current_label = labels[i]
            # log into source mailbox
            mailbox = ImapMailbox((server, current_label))
            sane_label = _sanitize_label(current_label)
            # process uids
            for uid in mailbox.search('UNDELETED'):
                Label.objects.create(migration=migration, uid=uid, label=sane_label)
            mailbox.close()
            if i + 1 == len(labels):
                # all labels processed
                migration.labels_processed = True
            else:
                # go to next label
                migration.current_label = labels[i + 1]
            migration.save()
            break
    
    return render_to_response("migration_process.html", {
        'migration': migration,
        'sane_label': sane_label,
    })