from django import template

register = template.Library()

def menu_item_row(context, menu, item, level=None):
    children = item.get_children()
    if level is None:
        level = 0
    else:
        level += 3
    return locals()
menu_item_row = register.inclusion_tag('admin/yama/menu/item_table_row.html',
                                       takes_context=True)(menu_item_row)
