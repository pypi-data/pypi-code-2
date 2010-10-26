

def sync_name(context, event):
    """ Sync first and last name with fullname
    """
    fullname_field = context.getField('fullname')
    firstname_field = context.getField('firstname')
    lastname_field = context.getField('lastname')
    if fullname_field and firstname_field and lastname_field:
        set_full = getattr(context, fullname_field.mutator)
        get_first = getattr(context, firstname_field.accessor) 
        get_last = getattr(context, lastname_field.accessor)
        set_full("%s %s" % (get_first(), get_last()))


