import Acquisition

class MaybeRedirectView(object):

    def __call__(self, **kwargs):
        error_type = kwargs.get('error_type', None)
        
        if error_type == 'NotFound':

            path = self.request.physicalPathFromURL(self.request.ACTUAL_URL)
            portal_path = self.context.portal_url.getPortalObject(
                ).getPhysicalPath()
            rel_path = '/'.join(path[len(portal_path):])
            query = [rel_path]

            if rel_path.startswith('/'):
                query.append(rel_path.lstrip('/'))
            else:
                query.append('/'+rel_path)

            if rel_path.endswith('/'):
                query.append(rel_path.rstrip('/'))
            else:
                query.append(rel_path+'/')

            results = self.context.portal_catalog(
                getLocalPath=query, Type='Redirect',
                sort_on='effective', sort_order='descending', sort_limit=1)

            if results:
                return self.request.response.redirect(
                    results[0].getRemoteUrl, status=301, lock=1)

        plone_templates = self.context.portal_skins.plone_templates
        return Acquisition.aq_base(
            plone_templates.standard_error_message).__of__(
            Acquisition.aq_inner(self.context))(**kwargs)
