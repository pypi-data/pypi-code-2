from zope.app.pagetemplate import ViewPageTemplateFile

render = ViewPageTemplateFile("table.pt")

def run():
    # collective.monkeypatcher is too clever to work here.
    from plone.app.content.browser.tableview import Table
    Table.render = render
