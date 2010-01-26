from qreature.interfaces import IQreatureSite, INewQreatureSiteEvent, IQreatureNews,IQreatureComment
from zope.app.container.btree import BTreeContainer
from zope.app.component.site import SiteManagerContainer
from zope.interface import implements
from zope.event import notify
from zope.schema.fieldproperty import FieldProperty

class QreatureSite(SiteManagerContainer, BTreeContainer):
    implements(IQreatureSite)
    def setSiteManager(self, site_manager):
        """ This method called from object added handler (see handlers)
        Firstly, I install SiteManager
        After: all folders and utilities via firing our custom event"""
        super(QreatureSite, self).setSiteManager(site_manager)
        notify(NewQreatureSiteEvent(self))
        
class NewQreatureSiteEvent(object):
    """ see interfaces. Its not a folder, but I put it here to avoid conflicts"""
    implements(INewQreatureSiteEvent)
    def __init__(self, site):
        self.object = site
        


class QreatureNews(BTreeContainer):
    implements(IQreatureNews)
    title = FieldProperty(IQreatureNews['title'])
    body = FieldProperty(IQreatureNews['body'])
    def __init__(self, title,body):
        self.title = title
        self.body = body
        super(QreatureNews,self).__init__()
    
class QreatureComment(BTreeContainer):
    implements(IQreatureComment)
    title = FieldProperty(IQreatureComment['title'])
    body = FieldProperty(IQreatureComment['body'])
    def __init__(self, title,body):
        self.title = title
        self.body = body
        super(QreatureComment,self).__init__()
        