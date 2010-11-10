from plone.app.portlets.manager import ColumnPortletManagerRenderer
from raptus.article.core.interfaces import IArticle

class ArticlePortletManagerRenderer(ColumnPortletManagerRenderer):
    
    @property
    def visible(self):
        if IArticle.providedBy(self.context):
            if self.manager.__name__=='plone.leftcolumn':
                hideLeftSlot  = self.context.Schema().get('hideLeftPortletslot').get(self.context)
                if hideLeftSlot:
                    return False
            if self.manager.__name__=='plone.rightcolumn':
                hideRightSlot = self.context.Schema().get('hideRightPortletslot').get(self.context)
                if hideRightSlot:
                    return False

        return super(ArticlePortletManagerRenderer, self).visible