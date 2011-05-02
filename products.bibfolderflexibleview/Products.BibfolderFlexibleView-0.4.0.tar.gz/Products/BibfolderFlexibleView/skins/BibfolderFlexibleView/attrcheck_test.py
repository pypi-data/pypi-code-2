catalog = context.portal_catalog
bibtool = context.portal_bibliography

#reftypyes = bibtool.getReferenceTypes()
print catalog(portal_type='ArticleReference', review_state='external')

return printed
